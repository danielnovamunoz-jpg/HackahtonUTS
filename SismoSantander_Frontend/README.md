# SismoSantander — Frontend React + Vite + TypeScript

Panel web para consumir la API FastAPI modular del proyecto SismoSantander. Incluye dashboard oscuro, mapa Leaflet, estadísticas, gráfico de categorías, tabla de municipios, exportación CSV y páginas de análisis y conexión.

## Requisitos
- Node.js 20 o superior recomendado
- npm
- API FastAPI modular ejecutándose

## Instalación en Windows (PowerShell)
Abre una terminal en esta carpeta y ejecuta:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Abre `http://localhost:5173`.

## Conectar con la API
Por defecto el frontend usa `http://127.0.0.1:8000`. La dirección se puede cambiar en `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Después de modificar `.env`, detén y vuelve a iniciar Vite. La API debe permitir solicitudes CORS desde `http://localhost:5173` (y `http://127.0.0.1:5173` si utilizas esa dirección).

## Ejecutar la API
En la carpeta de la API modular:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Si el entorno virtual no existe, créalo e instala sus dependencias según el README de la API.

## Vistas
- **Resumen general:** indicadores, mapa, distribución por categoría, municipios destacados y estado del modelo.
- **Mapa sísmico:** mapa interactivo con popups.
- **Municipios:** búsqueda y exportación CSV.
- **Análisis del modelo:** consulta los datos de `/modelo`, `/niveles`, `/fuentes` y `/salidas/resumen`.
- **Conexión API:** estado y dirección del servidor.

## Endpoints utilizados
`/salud`, `/municipios`, `/sismos`, `/geojson`, `/modelo`, `/niveles`, `/fuentes`, `/salidas/resumen`.

El frontend utiliza `Promise.allSettled`, por lo que puede mostrar los datos de endpoints que sí respondan aunque alguno falle. Los adaptadores intentan reconocer las formas comunes de respuesta; si la API devuelve una estructura diferente, revisa `src/services/api.ts` y `src/App.tsx`.

## Compilar para producción
```powershell
npm run build
npm run preview
```

## Notas
- No incluye datos sísmicos inventados: la interfaz se llena con las respuestas reales de la API.
- La capa base del mapa requiere conexión a internet para descargar los mosaicos de OpenStreetMap.
- Los resultados del modelo son analíticos y no constituyen alertas oficiales ni predicciones sísmicas.
