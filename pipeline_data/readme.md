# Pipeline de procesamiento sísmico SGC

Este proyecto automatiza la limpieza, normalización y transformación de los registros sísmicos del Servicio Geológico Colombiano (SGC). Su objetivo es consolidar múltiples archivos CSV crudos en un único dataset listo para análisis y entrenamiento de modelos de machine learning.

La lógica del pipeline incluye la lectura de varias descargas, la estandarización de columnas, la extracción de variables temporales y geográficas, y la generación de un dataset final con 22 variables clave.

## ¿Qué hace este proceso?

El sistema toma los archivos descargados desde la consulta experta del SGC, los unifica en un único conjunto de datos y prepara las variables necesarias para análisis exploratorio o modelado predictivo. Entre los pasos principales están:

- carga de múltiples CSVs
- detección y normalización de nombres de columnas
- conversión de fechas a formato temporal
- extracción de municipio y departamento a partir de la columna `Region`
- generación de variables adicionales como magnitud, profundidad y energía
- exportación del dataset final en formato CSV

## Formato de entrada esperado

Los archivos de entrada suelen tener una estructura similar a esta:

```csv
Fecha-Hora (UTC),Lat(°),Long(°),Prof(Km),Mag.,Tipo Mag.,Fases,Rms(Seg),Gap(°),Error Lat(Km),Error Long(Km),Error Prof(Km),Region,Estado
2019-03-02 00:01:57,6.687,-72.603,3.58,1.8,MLr_3,26,0.7,116,1.061,1.061,2.5,"Carcasí - Santander, Colombia",manual
```

## Nota importante sobre archivos Excel

Si los datos se descargan en formato `.xlsx`, suele incluirse información adicional en las primeras filas, como parámetros de la consulta. Antes de procesarlos, es recomendable:

1. abrir el archivo en Excel,
2. eliminar las primeras filas con metadatos,
3. dejar los encabezados en la fila 1,
4. guardar el archivo como `.csv`,
5. ubicarlo en la carpeta `data/datos_crudos/`.

Esto evita errores de lectura y mantiene la estructura original del dataset.

## Manejo de datos y restricciones

El pipeline incorpora varios controles para mantener la integridad del dataset:

- `Unificación de cabeceras`: detecta variaciones en nombres de columnas, como espacios dobles o diferencias de formato, y los estandariza internamente.
- `Limpieza temporal`: convierte fechas a formato de pandas y descarta registros no válidos.
- `Extracción geográfica`: identifica municipio y departamento a partir del texto contenido en la columna `Region`.
- `Feature engineering`: crea variables como magnitud categorizada, profundidad categorizada, energía calculada y distancia al nido sísmico.

## Requisitos

Instala las librerías necesarias en tu entorno virtual:

```bash
pip install pandas numpy
```

## Estructura del proyecto

```text
/
├── main.py
└── data/
    └── datos_crudos/
        ├── sismos_2018.csv
        └── sismos_2019.csv
```

## Cómo ejecutar el pipeline

Desde la raíz del proyecto, ejecuta:

```bash
python main.py
```

El script recorre todos los archivos de `data/datos_crudos/`, los combina y genera un dataset final en `data/dataset_maestro_22_variables.csv`.

## Salida esperada

El procesamiento genera un dataset estructurado con 22 variables, organizadas por categoría:

### Variables espaciales

- `departamento`
- `municipio`
- `latitud`
- `longitud`
- `dist_nido_sismico`

### Variables temporales

- `año`
- `mes`
- `dia`
- `hora`
- `es_noche`

### Variables físicas y energéticas

- `profundidad`
- `magnitud`
- `tipo_magnitud`
- `categoria_magnitud`
- `categoria_profundidad`
- `log_energia_joules`

### Variables técnicas e incertidumbre

- `fases`
- `Rms(Seg)`
- `Gap(°)`
- `Error Lat(Km)`
- `Error Long(Km)`
- `Error Prof(Km)`

## Resultado final

Al terminar la ejecución, se obtiene un dataset consolidado listo para ser usado en análisis exploratorio, clustering o modelos de aprendizaje automático.


---
<br>
<br>

## Ingeniería de características

La creación de las 22 variables maestras se fundamenta en transformaciones matemáticas y de texto implementadas en la función `procesar_sismos()`. A continuación se describen las principales métricas y reglas utilizadas:

### 1) Extracción geográfica

**`departamento` y `municipio`**  
La función `extraer_geo()` procesa la columna de texto libre `Region`. Utiliza el separador `-` y la coma `,` para aislar el nombre del municipio y del departamento, permitiendo obtener la geolocalización política del evento.

### 2) Variable cíclica: `es_noche`

Transforma la hora en una clasificación binaria:

- `1` = noche, si el evento ocurre entre las `18:00` y las `05:59`
- `0` = día, en cualquier otro caso

Esto ayuda a capturar patrones temporales asociados a la actividad sísmica.

### 3) Categorización sismológica

La discretización de variables continuas se realiza con `pd.cut()`, generando etiquetas interpretables:

#### Magnitud

- **Micro**: `< 3.0`
- **Menor**: `3.0 a 3.9`
- **Moderado**: `4.0 a 4.9`
- **Fuerte**: `>= 5.0`

#### Profundidad

- **Superficial**: `0 a 70 km`
- **Intermedio**: `70 a 300 km`
- **Profundo**: `> 300 km`

### 4) Normalización de energía

**`log_energia_joules`**  
Convierte la magnitud de Richter a energía física real mediante la ecuación de Gutenberg-Richter:

```text
E = 10^(1.5 * Magnitud + 4.8)
```

Luego, se aplica un logaritmo base 10:

```text
np.log10(E + 1)
```

Esta transformación normaliza la escala y evita que modelos basados en distancias, como `K-Means`, se sesguen por varianzas extremas.

### 5) Métrica de proximidad

**`dist_nido_sismico`**  
Calcula la distancia euclidiana plana utilizando el teorema de Pitágoras desde las coordenadas del sismo hasta el epicentro referencial del Nido Sísmico de Bucaramanga:

- latitud: `6.78`
- longitud: `-73.13`

Este indicador entrega una medida espacial útil para análisis geográficos y segmentación de clusters.
