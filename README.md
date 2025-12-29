# Juanma Football Analyser 🎥⚽
**Expo app para análisis de rendimiento en futbol femenino con Supabase, GPS tracking, datos de wearables y análisis de actividad en tiempo real.**

## 🎯 Características

✅ **Supabase Realtime** - Sincronización de partidos en tiempo real entre dispositivos
✅ **GPS Tracking** - Integración con proveedores externos (Strava, Catapult, etc.)
✅ **Wearables** - Datos de Whoop, relojes inteligentes (HR, strain, recuperación)
✅ **Análisis de Actividad** - Métricas de jugadoras (distancia, velocidad, aceleraciones)
✅ **Backups Automáticos** - 500MB storage gratuito en Supabase
✅ **Offline-first** - React Query cache para funcionamiento sin conexión
✅ **TypeScript** - Código tipado y escalable

## 🚀 Setup Rápido (5 minutos)

### 1. Clonar el repositorio
```bash
git clone https://github.com/juanmafdez8-arch/juanma-football-analyser.gitcd aigle-fc-analytics
cd juanma-football-analyser```

### 2. Crear archivo `.env.local`
```env
EXPO_PUBLIC_SUPABASE_URL=https://iwdgowrbcavknzkurpsk.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJ1IUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Instalar dependencias
```bash
npx expo install @supabase/supabase-js @tanstack/react-query-native lucide-react
```

### 4. Ejecutar la app
```bash
npx expo start
# Escanear QR con Expo Go
```

## 📂 Estructura del Proyecto

```
aigle-fc-analytics/
├── app.json                    # Configuración Expo
├── .env.local                  # Variables de entorno (Supabase)
├── src/
│   ├── app/
│   │   ├── index.tsx          # Home (lista de partidos)
│   │   ├── live-match.tsx     # Editor de partido en vivo
│   │   └── summary.tsx        # Resumen de estadísticas
│   ├── lib/
│   │   ├── supabase.ts        # Cliente Supabase + config
│   │   ├── gps-service.ts     # Integración con proveedores GPS
│   │   └── wearables.ts       # Parseo de datos Whoop/wearables
│   ├── hooks/
│   │   ├── useMatches.ts      # Hook Realtime para partidos
│   │   ├── useGPS.ts          # Hook para datos GPS
│   │   └── useWearables.ts    # Hook para datos de wearables
│   ├── types/
│   │   └── index.ts           # TypeScript tipos
│   └── components/
│       ├── MatchCard.tsx
│       ├── LiveMatchEditor.tsx
│       └── PerformanceChart.tsx
└── supabase/
    └── migrations/
        └── matches_table.sql   # Esquema de base de datos
```

## 🗄️ Esquema de Base de Datos (Supabase)

```sql
-- Tabla principal de partidos
CREATE TABLE matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  score JSONB DEFAULT '{"home": 0, "away": 0}',
  date TIMESTAMPTZ DEFAULT now(),
  actions JSONB[] DEFAULT '{}',
  gps_data JSONB,
  wearables_data JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Tabla de jugadoras
CREATE TABLE players (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  number INT,
  whoop_id TEXT,          -- ID para integración Whoop
  smartwatch_id TEXT,     -- ID del reloj inteligente
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Tabla de datos GPS (actualizaciones en tiempo real)
CREATE TABLE gps_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  latitude DECIMAL,
  longitude DECIMAL,
  speed DECIMAL,          -- km/h
  acceleration DECIMAL,   -- m/s²
  timestamp TIMESTAMPTZ DEFAULT now()
);

-- Tabla de datos de wearables
CREATE TABLE wearables_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
  heart_rate INT,         -- bpm
  strain_score DECIMAL,   -- Whoop strain 0-100
  recovery_score DECIMAL, -- Whoop recuperación 0-100
  calories_burned INT,
  timestamp TIMESTAMPTZ DEFAULT now()
);

-- Habilitar Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE matches, gps_tracking, wearables_data;
```

## 📱 Integración GPS (Proveedores Externos)

La app puede recibir datos GPS desde:

### **Strava API**
```typescript
// Importar GPX/FIT files de Strava
import { parseGPX } from '@lib/gps-service';
const gpsPoints = await parseGPX(file);
await supabase.from('gps_tracking').insert(gpsPoints);
```

### **Catapult Sports**
```typescript
// Webhook para recibir datos en tiempo real
// POST /api/webhooks/catapult
await processGPSData(req.body);
```

### **Formato Personalizado (CSV)**
```csv
timestamp,latitude,longitude,speed_kmh,acceleration
2025-01-04T10:30:00Z,48.8566,2.3522,15.5,2.3
```

## 🏆 Integración Wearables

### **Whoop**
```typescript
// Hook para sincronizar datos Whoop
const { strain, recovery, sleepData } = useWearables('whoop');

// Exportar CSV desde app Whoop:
// Settings > Export Data > Email
```

### **Smartwatches (Wear OS, Garmin, Amazfit)**
```typescript
// Sincronizar con Google Fit / Garmin Connect
const heartRateData = await fetchGoogleFitData();
await storewearablesData(heartRateData);
```

## 🔄 Workflows de Datos

### Workflow 1: Crear Partido + Agregar Datos GPS
1. Coach crea nuevo partido en app
2. App sincroniza con Supabase (realtime ✅)
3. Importar CSV de GPS desde empresa externa
4. CSV se parsea y almacena en tabla `gps_tracking`
5. Dashboard muestra heatmap de movimiento en tiempo real

### Workflow 2: Post-Partido Analysis
1. Finalizar partido → guardar en Supabase
2. Sincronizar datos Whoop de jugadoras
3. Cruzar datos: GPS + HR + Strain
4. Generar reporte PDF con estadísticas

## 📊 API Endpoints (Edge Functions - Supabase)

```typescript
// POST /functions/v1/import-gps
// Importar archivo CSV de GPS
{
  "match_id": "uuid",
  "csv_file": "..."
}

// POST /functions/v1/sync-whoop
// Sincronizar datos de Whoop
{
  "player_id": "uuid",
  "whoop_data": {...}
}
```

## 🔐 Seguridad

- **Row Level Security (RLS)** habilitado en Supabase
- Solo coaches pueden crear/editar partidos
- Datos de jugadoras protegidos (GDPR compliant)
- API keys en `.env.local` (nunca en git)

## 📈 Análisis Disponibles

- Distancia total recorrida por jugadora
- Velocidad máxima y promedio
- Aceleraciones/desaceleraciones
- Zona de frecuencia cardíaca
- Strain score (esfuerzo percibido)
- Recovery index (recuperación sugerida)
- Heatmaps de posicionamiento
- Comparativas intra-equipo

## 🚧 Roadmap

- [ ] Dashboard de análisis en tiempo real
- [ ] Predicción de lesiones (ML)
- [ ] Integración con VideoAssistant (Synergy Sports)
- [ ] Notificaciones de sobrecarga
- [ ] Export de reportes (PDF/Excel)
- [ ] Web dashboard (Next.js)
- [ ] Soporte para múltiples equipos

## 📚 Documentación

- [Supabase Docs](https://supabase.com/docs)
- [Expo Docs](https://docs.expo.dev)
- [React Query](https://tanstack.com/query/latest)
- [Whoop API](https://developer.whoop.com)
- [Strava API](https://developers.strava.com)

## 👨‍💻 Tech Stack

- **Frontend**: React Native / Expo Go
- **Backend**: Supabase (PostgreSQL)
- **Realtime**: WebSockets (Supabase Realtime)
- **State Management**: React Query
- **API Client**: Supabase JS SDK
- **Styling**: NativeWind / Tailwind

## 📝 Licencia

MIT License - Libre para uso personal y comercial

## 🤝 Contribuir

Pull requests bienvenidos. Para cambios mayores, abre un Issue primero.

---

**Hecho con ❤️ para Aigle FC - Análisis de Rendimiento en Fútbol Femenino**
