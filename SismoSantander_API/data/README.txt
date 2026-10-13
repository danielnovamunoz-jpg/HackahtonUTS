Coloca aquí el CSV de eventos sísmicos y nómbralo exactamente:
sismos.csv

Ruta esperada:
SismoSantander_API_Modular/data/sismos.csv

Columnas obligatorias:
municipio, latitud, longitud, profundidad, magnitud

Se recomienda conservar también las columnas originales:
departamento, año, mes, dia, hora, es_noche, tipo_magnitud, fases,
Rms(Seg), Gap(°), log_energia_joules, categoria_magnitud,
categoria_profundidad, dist_nido_sismico, Error Lat(Km), Error Long(Km),
Error Prof(Km).

La API no incluye datos sísmicos ficticios. Los resultados dependen del CSV real.
