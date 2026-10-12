# Insta Cleaner Pro — Windows Profile Counts Preview

**Paquete de prueba; no es un release estable.** Esta versión contiene la app HTML completa y el controlador del robot visible. La v120.41 pública no incluye Profile Counts.

## Uso automático (Windows)
1. Descomprime la carpeta completa y abre Start-Insta-Cleaner-Robot.cmd.
2. El lanzador abre Insta Cleaner y una ventana de Chrome en tu PC. Inicia sesión directamente en Instagram si no estaba abierta tu sesión.
3. El programa detectará tu propio perfil, abrirá el apartado Following, recorrerá los perfiles visibles y recopilará automáticamente sus contadores de seguidores y seguidos.
4. Las cifras irán apareciendo en Insta Cleaner → Insights → Profile Counts. No hace falta CSV de Instagram, pulsar Iniciar ni configurar el ritmo del robot. Las pausas internas son automáticas.
5. El programa reconoce la cuenta de Instagram y, si no coincide con el perfil seleccionado en Insta Cleaner, DETIENE la recolección para no mezclar tus datos. Si Instagram pide un desafío o bloquea las consultas, también se detiene.
6. Deja la PC encendida y la ventana del controlador abierta durante la recopilación. Los datos y pausas quedan guardados para reanudarlos al volver a abrir el lanzador.

**Importante:** esta es una build PREVIEW todavía no probada contra una sesión real de Instagram. Si cambia su interfaz, puede que el robot no encuentre el enlace Following o solo recupere una lista parcial. Nunca inventará números para suplir los faltantes.

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
