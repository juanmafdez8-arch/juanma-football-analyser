# 🎥 Analisis Automatico de Videos - Guia Completa

**Extrae automaticamente TODAS las metricas de futbol solo cargando el video del partido.**

## 📊 Que puedes obtener

✅ **Distancia recorrida por jugadora** (metros)
✅ **Velocidad maxima** (km/h)
✅ **Velocidad promedio** (km/h)
✅ **Numero de sprints detectados**
✅ **Heatmap de movimiento** (donde paso mas tiempo)
✅ **Aceleraciones/desaceleraciones**
✅ **Duracion del movimiento** (frames activos)

## 🚀 Instalacion (5 minutos)

### Paso 1: Instala Python 3.8+
```bash
# En Windows, descarga desde:
https://www.python.org/downloads/

# En Mac/Linux:
brew install python3
```

### Paso 2: Clona el repo
```bash
git clone https://github.com/juanmafdez8-arch/aigle-fc-analytics.git
cd aigle-fc-analytics
```

### Paso 3: Instala dependencias (primero descarga requirements.txt)
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar paquetes
pip install opencv-python mediapipe numpy
```

### Paso 4: Analiza tu video
```bash
python scripts/video-analyzer.py --video "tu_video.mp4" --output "resultados.json"
```

**Eso es todo!** ✨

## 📹 Ejemplo de uso

### Video ejemplo: Partido de 45 minutos
```bash
python scripts/video-analyzer.py \
  --video partido_aigle.mp4 \
  --output resultados_partido.json \
  --fps-sample 5
```

### Output (resultados_partido.json)
```json
{
  "video_info": {
    "duration_seconds": 2700,
    "fps": 30,
    "width": 1920,
    "height": 1080,
    "field_size_m": "105x68"
  },
  "players": {
    "player_0": {
      "total_distance_m": 8450.32,
      "max_speed_ms": 8.5,
      "avg_speed_ms": 4.2,
      "sprints_count": 24,
      "frame_count": 450
    },
    "player_1": {
      "total_distance_m": 9120.15,
      "max_speed_ms": 9.1,
      "avg_speed_ms": 4.5,
      "sprints_count": 31,
      "frame_count": 480
    }
  },
  "summary": {
    "total_players_detected": 22,
    "avg_distance_all_m": 8750.23,
    "total_sprints": 238
  }
}
```

## 🔧 Parametros avanzados

```bash
python scripts/video-analyzer.py \
  --video video.mp4 \
  --output resultados.json \
  --fps-sample 5          # Analizar cada 5 frames (mas rapido)
                           # --fps-sample 1 = analizar cada frame (mas preciso pero lento)
```

## ⚡ Velocidades de procesamiento

| Video | FPS Sample | Duracion | Tiempo Proceso |
|-------|-----------|----------|----------------|
| 45 min @ 30fps | 5 | 45 min | ~3-5 min |
| 90 min @ 30fps | 5 | 90 min | ~6-10 min |
| 45 min @ 30fps | 1 (preciso) | 45 min | ~25-40 min |

## 🎯 Casos de uso

### 1. Analizar rendimiento de una jugadora especifica
```python
import json
with open('resultados.json') as f:
    data = json.load(f)
    jugadora_1 = data['players']['player_1']
    print(f"Distancia: {jugadora_1['total_distance_m']}m")
    print(f"Velocidad max: {jugadora_1['max_speed_ms']*3.6:.1f} km/h")
    print(f"Sprints: {jugadora_1['sprints_count']}")
```

### 2. Subir resultados a Supabase
```python
import json
import requests

with open('resultados.json') as f:
    data = json.load(f)

# Para cada jugadora
for player_id, stats in data['players'].items():
    response = requests.post(
        'https://tu-proyecto.supabase.co/rest/v1/gps_tracking',
        json={
            'player_id': player_id,
            'match_id': 'match-uuid',
            'speed': stats['avg_speed_ms'],
            'distance': stats['total_distance_m'],
            'sprints': stats['sprints_count']
        },
        headers={'apikey': 'tu-anon-key'}
    )
```

### 3. Generar reporte PDF
```python
# Ver siguiente seccion
```

## 📊 Integrar con tu app Expo

### Opcion 1: Subir video → procesar → guardar en Supabase

```typescript
// En tu app Expo (TypeScript)
import * as FileSystem from 'expo-file-system';

const uploadVideoForAnalysis = async (videoUri: string, matchId: string) => {
  // 1. Subir video a Supabase Storage
  const uploadResponse = await fetch(
    `https://tu-proyecto.supabase.co/storage/v1/object/videos/${matchId}.mp4`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'video/mp4',
        'Authorization': `Bearer ${SUPABASE_TOKEN}`,
      },
      body: await FileSystem.readAsStringAsync(videoUri, { encoding: 'base64' }),
    }
  );
  
  // 2. Llamar a Edge Function para procesar video
  const analysisResponse = await fetch(
    `https://tu-proyecto.supabase.co/functions/v1/analyze-video`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SUPABASE_TOKEN}`,
      },
      body: JSON.stringify({
        match_id: matchId,
        video_path: `videos/${matchId}.mp4`,
      }),
    }
  );
  
  const results = await analysisResponse.json();
  return results; // { players: {...}, summary: {...} }
};
```

### Opcion 2: Crear Edge Function en Supabase (para procesar automaticamente)

```python
# supabase/functions/analyze-video/index.py
import functions_framework
import json
from video_analyzer import FootballVideoAnalyzer
from google.cloud import storage

@functions_framework.http
def analyze_video(request):
    request_json = request.get_json()
    video_path = request_json['video_path']
    match_id = request_json['match_id']
    
    # Descargar video de Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket('tu-bucket')
    blob = bucket.blob(video_path)
    blob.download_to_filename('/tmp/video.mp4')
    
    # Analizar
    analyzer = FootballVideoAnalyzer('/tmp/video.mp4')
    results = analyzer.analyze()
    results['match_id'] = match_id
    
    # Guardar en Supabase
    # ... (conexion a DB)
    
    return json.dumps(results)
```

## ⚠️ Requisitos del video

✅ **Formatos soportados**: MP4, MOV, AVI, MKV
✅ **Resolucion**: 720p minimo (recomendado 1080p)
✅ **FPS**: 24-60 fps (30fps ideal)
✅ **Duracion**: Sin limite
✅ **Vista**: Aerea/cenital (como camaras de estadio)
❌ **No funciona bien con**: videos de lado, muy bajos (piso), de noche sin iluminacion

## 🔧 Troubleshooting

### Error: "No module named 'cv2'"
```bash
pip install opencv-python
```

### Error: "No module named 'mediapipe'"
```bash
pip install mediapipe
```

### El script es muy lento
```bash
# Aumenta fps-sample a 10
python scripts/video-analyzer.py --video video.mp4 --fps-sample 10

# O convierte a 720p primero
ffmpeg -i video.mp4 -vf scale=1280:720 video_720p.mp4
python scripts/video-analyzer.py --video video_720p.mp4
```

### Detecta pocas jugadoras
- Asegurate de que la camara muestre el campo completo
- Los colores de las camisetas deben ser claros (rojo, azul, blanco)
- La iluminacion debe ser buena

## 📖 Proximo: Generar reportes PDF

Ver: `scripts/generate-report.py` (proximamente)

---

**Hecho para Aigle FC - Futbol Femenino** ⚽💪
