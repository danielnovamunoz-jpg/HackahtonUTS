# SismoSantander API — arquitectura modular

API REST con FastAPI que usa **exclusivamente el CSV proporcionado** para:
1. **Nivel 1 — HDBSCAN:** agrupar eventos sísmicos por proximidad espacial y profundidad para derivar fuentes.
2. **Nivel 2 — K-Means:** agrupar municipios según métricas agregadas de los eventos y variables derivadas del nivel 1.

> Los niveles son relativos al conjunto de municipios del CSV. No son predicciones de terremotos ni categorías oficiales de riesgo. La etiqueta “Nido de Bucaramanga” es heurística y debe validarse con criterio sismológico.

## Arquitectura

```text
SismoSantander_API_Modular/
├── app/
│   ├── main.py                    # Inicialización de FastAPI y ciclo de vida
│   ├── core/config.py             # Configuración centralizada por variables de entorno
│   ├── api/
│   │   ├── router.py              # Ensamble de rutas
│   │   ├── dependencies.py        # Dependencias HTTP
│   │   └── routes/                # Endpoints agrupados por dominio
│   ├── services/
│   │   ├── csv_service.py         # Lectura, validación y limpieza del CSV
│   │   ├── clustering_service.py  # HDBSCAN y agregación/K-Means
│   │   └── model_service.py       # Estado del modelo y recarga
│   └── utils/serialization.py    # Conversión segura a JSON
├── data/sismos.csv                # Añadir manualmente; no se incluyen datos privados
├── requirements.txt
├── .env.example
└── README.md
```

## Requisitos

- Python 3.11 recomendado.
- CSV con al menos estas columnas: `municipio`, `latitud`, `longitud`, `profundidad`, `magnitud`.
- Para HDBSCAN real: al menos 20 filas válidas e instalación correcta de `hdbscan`. Si no está disponible o hay pocos datos, se informa que se usó DBSCAN de respaldo.

## Instalación en Windows / PowerShell

Abre la terminal en la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copia el archivo CSV en `data` y llámalo `sismos.csv`. Luego inicia la API:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Si PowerShell bloquea la activación del entorno virtual, en esa terminal puedes ejecutar:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Verificar

- Swagger: http://127.0.0.1:8000/docs
- Estado: http://127.0.0.1:8000/salud
- Metadatos del modelo: http://127.0.0.1:8000/modelo
- Niveles: http://127.0.0.1:8000/niveles
- Municipios: http://127.0.0.1:8000/municipios
- Fuentes HDBSCAN: http://127.0.0.1:8000/fuentes
- Sismos: http://127.0.0.1:8000/sismos
- GeoJSON de puntos: http://127.0.0.1:8000/geojson
- Resumen: http://127.0.0.1:8000/salidas/resumen

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| GET | `/` | Estado básico y versión |
| GET | `/salud` | Estado de carga del CSV |
| POST | `/recargar` | Releer CSV y volver a entrenar |
| GET | `/modelo` | Metadatos, filas válidas, algoritmos y variables |
| GET | `/niveles` | Distribución de niveles relativos |
| GET | `/municipios` | Listado con filtros |
| GET | `/municipios/{nombre_o_codigo}` | Ficha del municipio y eventos destacados |
| GET | `/comparar?municipios=Bucaramanga,Girón` | Compara municipios |
| GET | `/zona-foco` | Resumen descriptivo de municipios de foco |
| GET | `/geojson` | Puntos GeoJSON, no polígonos |
| GET | `/fuentes` | Grupos de eventos detectados |
| GET | `/sismos` | Eventos con filtros |
| GET | `/variables` | Variables originales y derivadas |
| GET | `/validacion` | Resumen temporal descriptivo si hay año |
| GET | `/salidas/resumen` | Resumen consolidado |

## Ejemplos de filtros

```text
GET /municipios?nivel=Alto
GET /municipios?buscar=Floridablanca
GET /municipios?ordenar_por=magnitud_maxima&descendente=true
GET /sismos?mag_min=3&municipio=Los%20Santos&limite=100
GET /comparar?municipios=Bucaramanga,Girón,Piedecuesta
```

## Decisiones de diseño

- **Separación de responsabilidades:** rutas HTTP no contienen la lógica de entrenamiento; servicios se ocupan de lectura y modelos.
- **Configuración centralizada:** rutas del CSV y parámetros de referencia pueden ajustarse con variables de entorno.
- **Validación de datos:** columnas requeridas, conversión numérica, coordenadas válidas y eliminación de registros incompletos.
- **Serialización segura:** NaN e infinitos se convierten a `null` para respuestas JSON.
- **Errores legibles:** si el CSV no carga, los endpoints de datos responden 503 con el detalle del problema.
- **CORS restringido por defecto:** localhost para Vite. Ajusta `CORS_ORIGINS` para otros orígenes.
- **Reproducibilidad:** K-Means usa `random_state=42` y `n_init=20`.

## Limitaciones metodológicas

- Las coordenadas se proyectan aproximadamente a kilómetros para el clustering.
- La etiqueta del Nido se deriva de profundidad y distancia a una coordenada de referencia; no sustituye una identificación geológica.
- K-Means asigna niveles relativos según las características disponibles. Los niveles no deben presentarse como riesgo oficial.
- El CSV no contiene polígonos municipales, por lo que `/geojson` devuelve puntos aproximados.
- `/validacion` ofrece estadísticas descriptivas; no afirma capacidad predictiva futura.
- La ruta `/clasificar` no se incluye en esta versión modular para evitar presentar una clasificación ad hoc como predicción sin validación independiente.

## Integración con React + Vite

Ejemplo:

```ts
const API_URL = "http://127.0.0.1:8000";

const response = await fetch(`${API_URL}/municipios`);
if (!response.ok) throw new Error("No se pudieron cargar los municipios");
const data = await response.json();
console.log(data.municipios);
```
