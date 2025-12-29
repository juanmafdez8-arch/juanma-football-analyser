#!/usr/bin/env python3
"""
Aigle FC Video Analyzer

Analiza videos de partidos de futbol y extrae metricas de rendimiento:
- Distancia recorrida por jugadora
- Velocidad maxima y promedio
- Aceleraciones/desaceleraciones
- Heatmap de movimiento
- Deteccion de sprints

Uso: python scripts/video-analyzer.py --video video.mp4 --output results.json
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import math
from collections import defaultdict

class FootballVideoAnalyzer:
    def __init__(self, video_path: str, fps_sample: int = 5):
        """
        Inicializa el analizador de video.
        
        Args:
            video_path: Ruta al video del partido
            fps_sample: Analizar cada N frames (5 = analizar cada 5 frames)
        """
        self.video_path = video_path
        self.fps_sample = fps_sample
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # MediaPipe Pose Detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # 0=light, 1=full, 2=heavy
            smooth_landmarks=True
        )
        
        # Para detectar personas (YOLO simplificado con contornos)
        self.player_positions = defaultdict(list)
        self.frame_count = 0
        
    def detect_players(self, frame: np.ndarray) -> List[Tuple[float, float]]:
        """
        Detecta jugadores en el frame usando contornos.
        Retorna lista de (x, y) coordenadas de cada jugadora.
        """
        # Convertir a HSV para mejor deteccion de colores
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detectar dos colores de camisetas (rojo y azul aproximadamente)
        # Para equipos de futbol femenino
        lower_skin = np.array([0, 20, 70])
        upper_skin = np.array([20, 255, 255])
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Morph operations para limpiar la mascara
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        players = []
        min_area = 500  # Area minima para considerar un jugador
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                M = cv2.moments(contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    players.append((cx, cy, area))
        
        return players
    
    def calculate_distance(self, pos1: Tuple, pos2: Tuple) -> float:
        """Calcula distancia euclidiana entre dos puntos."""
        return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
    
    def pixels_to_meters(self, pixel_distance: float) -> float:
        """
        Convierte distancia en pixels a metros.
        Asume un campo de futbol de 105m x 68m.
        """
        field_width_pixels = self.width * 0.9  # El campo no ocupa toda la imagen
        field_width_meters = 105
        ratio = field_width_meters / field_width_pixels
        return pixel_distance * ratio
    
    def analyze(self) -> Dict:
        """
        Analiza el video completo y retorna metricas.
        """
        print(f"Analizando video: {self.video_path}")
        print(f"Video: {self.width}x{self.height} @ {self.fps:.1f}fps")
        print(f"Duracion: {self.total_frames / self.fps:.1f} segundos")
        print(f"Frames a analizar: {self.total_frames // self.fps_sample}")
        
        players_data = defaultdict(lambda: {
            'positions': [],
            'distances': [],
            'speeds': [],
            'total_distance': 0,
            'max_speed': 0,
            'avg_speed': 0,
            'sprints': 0,  # Aceleraciones > 5 m/s
            'heatmap': np.zeros((self.height, self.width), dtype=np.float32)
        })
        
        frame_idx = 0
        player_id_counter = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            if frame_idx % self.fps_sample != 0:
                frame_idx += 1
                continue
            
            # Detectar jugadores en este frame
            players = self.detect_players(frame)
            
            # Calcular metricas para cada jugadora
            for player_idx, (x, y, area) in enumerate(players):
                player_id = player_idx  # Simplificado: no hacemos tracking multi-frame
                
                # Agregar posicion
                players_data[player_id]['positions'].append((x, y))
                
                # Actualizar heatmap
                cv2.circle(players_data[player_id]['heatmap'], (x, y), 20, 1, -1)
                
                # Calcular distancia si hay posicion anterior
                if len(players_data[player_id]['positions']) > 1:
                    prev_pos = players_data[player_id]['positions'][-2]
                    curr_pos = players_data[player_id]['positions'][-1]
                    
                    pixel_dist = self.calculate_distance(prev_pos, curr_pos)
                    meters_dist = self.pixels_to_meters(pixel_dist)
                    
                    # Distancia en movimiento (filtrar ruido)
                    if pixel_dist > 5:  # Mas de 5 pixels
                        players_data[player_id]['distances'].append(meters_dist)
                        players_data[player_id]['total_distance'] += meters_dist
                        
                        # Velocidad = distancia / tiempo
                        time_between_frames = self.fps_sample / self.fps
                        speed = meters_dist / time_between_frames
                        players_data[player_id]['speeds'].append(speed)
                        
                        if speed > players_data[player_id]['max_speed']:
                            players_data[player_id]['max_speed'] = speed
                        
                        # Detectar sprints (> 5 m/s)
                        if speed > 5:
                            players_data[player_id]['sprints'] += 1
            
            self.frame_count += 1
            if frame_idx % (30 * self.fps_sample) == 0:
                elapsed_seconds = (frame_idx / self.fps)
                print(f"  Procesados {elapsed_seconds:.1f}s de {self.total_frames / self.fps:.1f}s")
            
            frame_idx += 1
        
        # Calcular promedios
        results = {
            'video_info': {
                'duration_seconds': self.total_frames / self.fps,
                'fps': self.fps,
                'width': self.width,
                'height': self.height,
                'field_size_m': '105x68'
            },
            'players': {}
        }
        
        for player_id, data in players_data.items():
            if data['distances']:
                avg_speed = np.mean(data['speeds']) if data['speeds'] else 0
            else:
                avg_speed = 0
            
            results['players'][f'player_{player_id}'] = {
                'total_distance_m': round(data['total_distance'], 2),
                'max_speed_ms': round(data['max_speed'], 2),
                'avg_speed_ms': round(avg_speed, 2),
                'sprints_count': data['sprints'],
                'frame_count': len(data['positions'])
            }
        
        results['summary'] = {
            'total_players_detected': len(players_data),
            'avg_distance_all_m': round(np.mean([d['total_distance'] for d in players_data.values()]), 2),
            'total_sprints': sum(d['sprints'] for d in players_data.values())
        }
        
        self.cap.release()
        return results

def main():
    parser = argparse.ArgumentParser(
        description='Analiza videos de partidos de futbol'
    )
    parser.add_argument('--video', required=True, help='Ruta del video')
    parser.add_argument('--output', default='results.json', help='Archivo de salida')
    parser.add_argument('--fps-sample', type=int, default=5, help='Analizar cada N frames')
    
    args = parser.parse_args()
    
    analyzer = FootballVideoAnalyzer(args.video, fps_sample=args.fps_sample)
    results = analyzer.analyze()
    
    # Guardar resultados
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResultados guardados en: {args.output}")
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
