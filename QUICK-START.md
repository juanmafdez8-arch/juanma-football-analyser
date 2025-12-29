# ⚡ Quick Start - 5 Minutos

**Solo 4 pasos para analizar tu primer video de futbol**

## 1️⃣ Instala Python (si no lo tienes)

```bash
# Windows: Descarga desde https://www.python.org/downloads/
# Mac: brew install python3
# Linux: sudo apt install python3
```

## 2️⃣ Clona el repositorio

```bash
git clone https://github.com/juanmafdez8-arch/aigle-fc-analytics.git
cd aigle-fc-analytics
```

## 3️⃣ Instala paquetes

```bash
pip install opencv-python mediapipe numpy
```

## 4️⃣ Analiza tu video

```bash
python scripts/video-analyzer.py --video "tu_video.mp4" --output "resultados.json"
```

**¡Listo!** 🎉 Los resultados estaran en `resultados.json`

---

## 📊 Que obtendras

```json
{
  "players": {
    "player_0": {
      "total_distance_m": 8450,      // Distancia en metros
      "max_speed_ms": 8.5,           // Velocidad maxima
      "avg_speed_ms": 4.2,           // Velocidad promedio  
      "sprints_count": 24            // Numero de sprints
    }
  },
  "summary": {
    "total_players_detected": 22,    // Jugadoras detectadas
    "avg_distance_all_m": 8750       // Distancia promedio equipo
  }
}
```

---

## 🎬 Requisitos del video

✅ Formato: MP4, MOV, AVI, MKV  
✅ Resolucion: 720p minimo  
✅ FPS: 24-60  
✅ Vista: Aerea (como camaras de estadio)  

---

## 📚 Documentacion completa

Ver: [`VIDEO-ANALYSIS-GUIDE.md`](./VIDEO-ANALYSIS-GUIDE.md)

---

## ❓ Problemas?

### Error: "No module named 'cv2'"
```bash
pip install opencv-python
```

### Error: "No module named 'mediapipe'"
```bash
pip install mediapipe
```

### Muy lento
```bash
python scripts/video-analyzer.py --video video.mp4 --fps-sample 10
```

---

## 📈 Proximo paso

1. Sube los resultados JSON a tu app Expo
2. Integra con Supabase para guardar historicamente
3. Genera reportes PDF con estadisticas

Ver README.md para setup completo.
