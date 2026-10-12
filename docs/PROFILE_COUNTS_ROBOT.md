# Profile Counts — robot navegador y estadísticas por perfil

**Estado:** desarrollo en la rama feature; **no publicado**. Diseño solicitado el 11 de octubre de 2026. Esta función no confunde el número de cuentas que **tú** sigues con los Followers/Following de **cada tercero**.

## Control directo desde Insta Cleaner (PC, sin intercambio manual de CSV)

El **robot local de PC** se puede controlar desde la sección **Insights → Profile Counts**. Usa un servidor HTTP de bucle local (solo `127.0.0.1`) protegido con una clave aleatoria de un solo inicio, que no es la contraseña de Instagram ni una API de Meta.

1. Instala una vez los requisitos `python -m pip install playwright` y `python -m playwright install chromium`.
2. Ten descargado el HTML de **la versión de desarrollo que incluye Profile Counts**. La versión pública v120.41 todavía NO incluye esta función.
3. Con una terminal en el código de Insta Cleaner, arranca:

```bash
python tools/profile_counts_bridge.py --app "RUTA/IG-Cleaner-Pro-Desktop.html"
```

4. Se abre tu HTML de Insta Cleaner en el navegador. Carga Following si hace falta, entra a Insights y configura **Perfiles máximos**, **Cada (minutos)** y **Espera entre perfiles (segundos)**. Pulsa **Iniciar recopilación**.
5. Cuando se abra Chromium para Instagram, inicia sesión **directamente allí**. Regresa a Insta Cleaner y pulsa **Ya inicié sesión**. La recopilación guarda resultados continuamente y aparecen en la tabla sin transferencias CSV.
6. Puedes pulsar **Pausar robot**, cerrar la app y luego volver a iniciar el puente para continuar. En Insights, **Recuperar guardados** consulta los resultados persistentes sin abrir Instagram, y la barra de avance muestra el porcentaje de perfiles con ambas cifras obtenidas. La PC y la terminal del puente deben seguir abiertas mientras el robot trabaja. Los resultados se guardan separados por propietario de IG Cleaner y perfil de Instagram. El siguiente inicio no repite registros completados.

La clave del puente aparece únicamente en el fragmento del enlace local de lanzamiento. **No compartas el enlace**, ni el directorio de Chromium con sus cookies. El puente no se expone a Internet ni ejecuta un servidor remoto. Cierra la terminal para apagarlo.

El CSV sigue existiendo como alternativa portátil, especialmente para importar resultados en Android. Android no ejecuta Playwright/Chromium Desktop ni continúa recopilando mientras está cerrado; la consulta es desde la computadora.

### Control visible y limitaciones

- Programación independiente: **máximo de 1–10,000 perfiles por ventana móvil** (1–1,440 minutos), y **espera mínima de 0–3,600 segundos** entre inicios de consulta. Predeterminado: 50 visitas por 60 minutos y 72 segundos entre perfiles. No garantiza que Instagram responda ni evita restricciones.
- Ejemplo pedido: **200 perfiles cada 5 minutos** con **5 segundos entre perfiles** equivale aproximadamente a **hasta 60 inicios por 5 minutos** (y potencialmente menos debido a la carga de páginas). Ambos límites se cumplen simultáneamente; no se aceleran las visitas para alcanzar los 200.
- Las visitas consumen presupuesto antes de abrir el perfil y se registran en el archivo local `.visits.json` correspondiente a la cuenta. El historial no se borra al pausar/reiniciar. Los errores y páginas bloqueadas consumen también una visita; no se restaura el cupo para insistir artificialmente.
- Al aparecer desafío, login o bloqueo, el robot **se detiene** sin evasión automática.
- Los contadores redondeados que muestre Instagram se etiquetan como aproximados; ausencia no es cero.
- Una nueva sesión del puente no borra cuentas ni datos, pero el almacenamiento local de navegadores distintos puede diferir. Usa **el mismo HTML y perfil de navegador** que tu Insta Cleaner habitual.

## Qué hace

Desde **Insights → Profile Counts**:

1. Carga/sincroniza Following del Instagram activo, como de costumbre.
2. Pulsa **Exportar cola para robot**. Descarga CSV con `username,profile_url`.
3. En una computadora ejecuta el robot (debajo) usando tu propia sesión normal de navegador.
4. El robot visita perfiles visibles, interpreta la cifra **Followers/Seguidores** y **Following/Siguiendo** de cada uno, guarda al instante en `resultados.csv` y espera entre perfiles.
5. Vuelve a **Insights → Importar resultados CSV**. La tabla mostrará usuarios, ambas cifras, fecha, estado y valor aproximado si Instagram solo mostró “12.3K”.
6. Si reinicias el robot con el mismo CSV de resultados, omite los que ya tienen registro. Usa `--retry-unavailable` para reintentar errores (no repite los OK).

**No hace falta solicitar acceso a la API de Instagram.** Sí necesitarás iniciar sesión personalmente en el navegador local la primera vez; la app no lee tu contraseña. La carpeta del perfil del navegador contiene cookies de sesión: no la compartas ni la subas a GitHub. Los resultados quedan en archivos locales y en el espacio local separado por propietario de IG Cleaner y cuenta Instagram.

### Instalación en Windows / macOS / Linux

Requiere Python 3 y el repositorio IG Cleaner Pro en la PC:

```bash
python -m pip install playwright
python -m playwright install chromium
python tools/profile_counts_robot.py --input ig-cleaner-cola-legacy.csv --output resultados.csv --per-hour 50
```

Cambia el nombre `ig-cleaner-cola-legacy.csv` por el archivo descargado. La primera vez se abre una ventana de Chromium; inicia sesión en Instagram ahí, regresa a la terminal y presiona **Enter**. No cierres esa terminal ni el navegador mientras recolecta. Dejar la PC suspendida detiene el trabajo. También puedes personalizar la cadencia con `--max-per-window 200 --window-minutes 5 --min-delay-seconds 5`. Si se omiten, se aplica la configuración predeterminada de 50/60 minutos y espera de 72 segundos. `--per-hour` se conserva para compatibilidad antigua con la cuota por hora, pero los tres argumentos nuevos son los recomendados. Son techos de visitas, no garantías de resultados ni un método para eludir restricciones.

Para procesar únicamente veinte perfiles en una sesión:

```bash
python tools/profile_counts_robot.py --input ig-cleaner-cola-legacy.csv --output resultados.csv --max-per-window 20 --window-minutes 60 --min-delay-seconds 180 --max-profiles 20
```

El archivo `resultados.csv` es incremental y se puede importar repetidamente sin eliminar los datos previos. Si deseas retomar la cola, utiliza exactamente los mismos `--input`, `--output` y `--session-dir` (el último usa una ruta privada predeterminada).

## Límites verificables

- El robot corre localmente en PC (puede controlarse desde el HTML mediante el puente local). No es un proceso Android en segundo plano ni un servicio en la nube.
- Se leen **etiquetas visibles del perfil**, no endpoints privados, cookies ajenas, listas detalladas de seguidores ni contraseñas.
- Se detiene al encontrar solicitudes de autenticación, desafíos o indicios de bloqueo. No resuelve CAPTCHA, no evade controles ni hace follow/unfollow.
- Las cifras pueden ser aproximadas en la interfaz de Instagram; se guardan con `approximate=true` y se marcan con ≈. Si no hay dos números legibles, el estado será `unavailable` (vacío), **nunca cero inventado**.
- La automatización de visitas puede infringir condiciones de Instagram y causar limitaciones de acceso incluso a baja velocidad. Revisar https://www.facebook.com/legal/automated_data_collection_terms .
- Aún no se probó con la cuenta real del propietario ni contra la interfaz en vivo de Instagram. El DOM, textos y política de la plataforma pueden cambiar sin aviso.
- Los datos quedan locales en cada instalación. La sincronización automática de estos nuevos contadores Desktop↔Android aún no está implementada; el puente sí sincroniza directamente los datos locales de la app de escritorio. En Android podrán consultarse al importar el CSV mediante el Workspace integrado, sujeto a pruebas en WebView.
- El importador solo acepta filas cuya columna `username` existe en Following activo y fecha válida; evita mezclar perfiles de Instagram diferentes. Exporta CSV desde la cuenta correcta.

## Formato de resultados

```csv
username,followers,following,checked_at,source,status,approximate
ejemplo,1234,567,2026-10-11T23:30:00+00:00,instagram_visible_profile_browser,ok,false
```

Estados: `ok` — ambas cifras leídas; `unavailable` — no visibles; `error` — error de página/conexión. Los perfiles sin visitar siguen pendientes en Insta Cleaner y no generan datos falsos.

## QA requerida antes de publicar

- Tests unitarios de conversión numérica de HTML visible, separadores y ausencia de cifras; lectura/reanudación CSV.
- UI Chromium con ZIP de Following real de prueba y CSV de resultado; independencia de propietario y `account_key`.
- Android: importar y mostrar CSV a través de WebView en dispositivo/emulador, conservando auth, Focus y datos anteriores.
- Verificar empaquetado del HTML actualizado y las instrucciones de instalación; no publicar ni alterar la firma Android antes del release coordinado y autorizado.
