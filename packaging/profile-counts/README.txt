# Insta Cleaner Pro — Automatizaciones + Profile Counts (Windows Preview)

**Paquete de prueba; no es un release estable.** Verifica el archivo `BUILD-INFO.txt` para conocer el commit exacto del candidato. Contiene la app HTML completa y un controlador local de Chrome para Profile Counts y Automatizaciones. La estable pública v120.42 tiene Profile Counts, pero no el motor de acciones de este candidato.

## Uso local (Windows)

1. Descomprime el ZIP COMPLETO y abre `Start-Insta-Cleaner-Robot.cmd`. No ejecutes el HTML suelto: las acciones necesitan el robot local conectado.
2. Inicia sesión en **IG Cleaner Pro** y selecciona el **Instagram correcto** con @username asignado.
3. **Para Profile Counts:** abre Insights → Profile Counts y pulsa **Conectar Instagram / abrir Chrome**. Inicia sesión directamente en la ventana real de Instagram. Configura tus tandas/esperas y usa Pausar o Reanudar; consulta el avance y los errores dentro de la app.
4. **Para Cancelar solicitudes enviadas:** importa tu lista Pending Requests desde un export de Instagram. Abre Automatizaciones → Cancelar solicitudes, revisa los perfiles, marca Omisiones/Favoritos, define tamaño de tanda e intervalos, pulsa **Ejecutar tanda seleccionada** y confirma. El robot solo actúa en perfiles que todavía muestran **Requested/Solicitado**.
5. **Para Dejar de seguir:** importa exportaciones completas de Following y Followers, no HTML parcial. En Automatizaciones → Dejar de seguir, revisa la cola, protegidos, tamaños y espera. Pulsa **Ejecutar tanda seleccionada** y confirma. El robot requiere botón **Following/Siguiendo** en el perfil real y confirma estado final **Follow/Seguir**.
6. **Pausar/Reanudar:** el controlador guarda un historial por Instagram/tarea y un registro de tiempo consumido; no repite acciones confirmadas ni vuelve a clicar perfiles con resultado ambiguo. Los cambios de cuenta o bloqueos detienen el proceso.
7. Los **Mutuals** solo tienen Focos: nunca se cancelan ni dejan de seguir automáticamente desde esa sección.

**Limitación de la vista previa:** código y pruebas automatizadas no sustituyen un test presencial con tu Instagram. El DOM y los botones de Instagram pueden cambiar o variar por idioma. Si el robot no consigue identificar el perfil, el estado o el control final, **NO realiza la acción** (o marca para revisar si ya hubo un clic). Es posible que Instagram restrinja la cuenta por automatización, incluso con pausas.

**Versión:** esta compilación candidata lleva la interfaz y el motor de acciones nuevos; los ZIP anteriores de v120.42 no los incluyen. No equivale a un release estable.

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
