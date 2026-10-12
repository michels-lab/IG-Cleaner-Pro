# Insta Cleaner Pro — Aplicación Windows integrada (Preview)

**Paquete de prueba; no es un release estable.** Verifica el archivo `BUILD-INFO.txt` para conocer el commit exacto del candidato. Contiene un único InstaCleanerPro.exe con la interfaz y el robot integrados. La estable pública v120.42 no contiene esta integración.

## Inicio único en Windows (sin .cmd ni programa auxiliar)

1. Extrae el ZIP completo y haz doble clic en **InstaCleanerPro.exe**. Es la aplicación completa con su interfaz y el motor del robot integrados; no abras un HTML ni ejecutes un .cmd.
2. Insta Cleaner abre una **ventana de aplicación**, sin las pestañas habituales de Chrome. Inicia sesión en IG Cleaner y selecciona tu perfil de Instagram. En el primer arranque se crea un espacio local persistente específico para esta aplicación.
3. En **Automatizaciones**, elige Cancelar solicitudes enviadas o Dejar de seguir a quienes no te siguen. Revisa la cola y los perfiles protegidos, elige tamaños de tanda, descansos e intervalos, y pulsa **Ejecutar tanda seleccionada**. La app solicita tu aprobación antes de efectuar cambios.
4. El robot se inicia **dentro del mismo InstaCleanerPro.exe** al ejecutar una tarea. Cuando necesite tu sesión de Instagram abrirá una ventana visible de Chrome, donde puedes iniciar sesión en el sitio auténtico; no se introducen contraseñas de Instagram en Insta Cleaner.
5. **Pausar** y **Reanudar** funcionan desde la app. Hay progreso, errores y lista de resultados; no se repiten acciones confirmadas ni clics ambiguos. Favoritos/Omitir se comprueban antes de actuar. Cerrar la aplicación solicita una pausa y espera a que el robot finalice el punto seguro.
6. En **Insights → Profile Counts** se conecta la sesión de Instagram de manera equivalente para recopilar las cifras públicas. **Mutuals** conserva exclusivamente Focos humanos; nunca ejecuta unfollows o cancelaciones.

**IMPORTANTE:** Esta es una preview técnica, no una release estable. Las pruebas de GitHub son sobre navegadores con páginas simuladas. No se ha probado todavía con una sesión real del propietario; empieza con una tanda de 1 o 2 cuentas que quieras modificar conscientemente y comprueba el resultado. Instagram puede cambiar sus controles o restringir automatizaciones. Nunca intentes eludir verificaciones o restricciones.

**Persistencia y actualización:** La interfaz integrada y sus datos se almacenan bajo `%LOCALAPPDATA%\Michels Lab\Insta Cleaner Pro\` y se mantienen en actualizaciones del mismo EXE. Los datos anteriores de una versión HTML en una ruta distinta **no se migran automáticamente**: expórtalos como respaldo e impórtalos en la nueva aplicación antes de hacer cambios; no borres el HTML viejo hasta confirmar que todo está presente. El robot sigue utilizando los datos existentes de `%USERPROFILE%\.ig-cleaner-pro\` para no perder sesiones o resultados previos.

## Datos y límites
- **No solicita credenciales a Insta Cleaner** ni usa la API de Meta. La contraseña de Instagram se escribe únicamente en la ventana auténtica de Chrome que abre el robot.
- Google Chrome y el controlador solo se comunican a través de un servicio privado en `127.0.0.1`; el enlace local de lanzamiento contiene una clave temporal. No lo compartas.
- La primera ejecución de una aplicación Windows no firmada puede mostrar advertencia del sistema. **No desactives tu antivirus ni protecciones de Windows** para usarla. Si no confías en la procedencia, no la ejecutes.
- Browser login: `%USERPROFILE%\.ig-cleaner-pro\instagram-browser` (cookies privadas, no compartir). Resultados: `%USERPROFILE%\.ig-cleaner-pro\profile-counts` (CSV persistentes; evitar borrarlos).
- El workspace de Insta Cleaner almacena otra parte de la información localmente. **Mover el HTML o usar otro perfil/navegador puede mostrar datos diferentes**. Guarda respaldos de tus listas y utiliza siempre la misma ubicación para abrirla.
- Ejemplo configurable: máximo de 200 visitas en una ventana de 5 minutos, con 5 segundos entre perfiles (equivale a no más de unas 60 consultas en cinco minutos, antes de contar la carga de páginas). Adicionalmente se puede programar una pausa de 5 minutos **después de completar cada 200 visitas**, si así lo decides.
- El registro local conserva los límites y descansos tras pausar o reiniciar; no reinicia la cuenta de visitas. Las visitas automáticas pueden estar restringidas por las condiciones de Instagram y provocar desafíos o restricciones, incluso con pausas. No se evaden restricciones ni se garantizan respuestas.
- Los resultados solo se integran automáticamente en la app HTML de PC. La transferencia Desktop↔Android de esta nueva tabla aún está pendiente; los CSV siguen disponibles.
- **No probado aún con una sesión real de Instagram ni en el equipo Windows del usuario.** Es una build de validación técnica.

## Validación técnica
La build Windows ejecuta `IGCleanerProfileCounts.exe --healthcheck` en un runner Windows sin abrir Instagram, para confirmar que el ejecutable congelado puede importar Playwright e iniciar un servidor local. Esto **no sustituye** la prueba en navegador Chrome real ni Android.
