# Insta Cleaner Pro — Windows Profile Counts Preview

**Paquete de prueba; no es un release estable.** Esta versión contiene la app HTML completa y el controlador del robot visible. La v120.41 pública no incluye Profile Counts.

## Uso (Windows)
1. Descomprime toda la carpeta, sin separar los archivos.
2. Necesitas Google Chrome instalado (el robot abre Chrome visible), conexión a Internet y una cuenta Instagram propia. No necesitas instalar Python, Playwright ni ejecutar comandos.
3. Haz doble clic en `Start-Insta-Cleaner-Robot.cmd`. Mantén abierta la ventana del controlador y utiliza el navegador que se abrirá con Insta Cleaner.
4. En Insta Cleaner, importa/sincroniza tu Following habitual; cambia al Instagram correcto y ve a **Insights → Profile Counts**.
5. Configura **máximo de perfiles**, **ventana en minutos**, **espera mínima después de cada perfil (segundos)** y, opcionalmente, **descansar X minutos después de cada N perfiles**. Se guardan por cuenta de Instagram. Pulsa **Iniciar recopilación**, inicia sesión en Instagram personalmente si hace falta y pulsa **Ya inicié sesión** en la app.
6. Consulta la tabla mientras avanzan las visitas. **Pausar robot** conserva registros guardados; puedes volver a abrir este lanzador y reanudar con el mismo perfil/propietario.

## Datos y límites
- **No solicita credenciales a Insta Cleaner** ni usa la API de Meta. La contraseña de Instagram se escribe únicamente en la ventana auténtica de Chrome que abre el robot.
- Google Chrome y el controlador solo se comunican a través de un servicio privado en `127.0.0.1`; el enlace local de lanzamiento contiene una clave temporal. No lo compartas.
- La primera ejecución de una aplicación Windows no firmada puede mostrar advertencia del sistema. **No desactives tu antivirus ni protecciones de Windows** para usarla. Si no confías en la procedencia, no la ejecutes.
- Browser login: `%USERPROFILE%\.ig-cleaner-pro\instagram-browser` (cookies privadas, no compartir). Resultados: `%USERPROFILE%\.ig-cleaner-pro\profile-counts` (CSV persistentes; evitar borrarlos).
- El workspace de Insta Cleaner almacena otra parte de la información localmente. **Mover el HTML o usar otro perfil/navegador puede mostrar datos diferentes**. Guarda respaldos de tus listas y utiliza siempre la misma ubicación para abrirla.
- Ejemplo configurable: máximo de 200 visitas en una ventana de 5 minutos, con 5 segundos entre perfiles (equivale a no más de unas 60 consultas en cinco minutos, antes de contar la carga de páginas). Adicionalmente se puede programar una pausa de 5 minutos **después de completar cada 200 visitas**, si así lo decides.
- El registro local conserva los límites y descansos tras pausar o reiniciar; no reinicia la cuenta de visitas. La automatización puede estar restringida por las condiciones de Instagram y provocar desafíos o restricciones, incluso con pausas. No se evaden restricciones ni se garantizan respuestas.
- Los resultados solo se integran automáticamente en la app HTML de PC. La transferencia Desktop↔Android de esta nueva tabla aún está pendiente; los CSV siguen disponibles.
- **No probado aún con una sesión real de Instagram ni en el equipo Windows del usuario.** Es una build de validación técnica.

## Validación técnica
La build Windows ejecuta `IGCleanerProfileCounts.exe --healthcheck` en un runner Windows sin abrir Instagram, para confirmar que el ejecutable congelado puede importar Playwright e iniciar un servidor local. Esto **no sustituye** la prueba en navegador Chrome real ni Android.
