# Automatizaciones — especificación y estado

**Estado 2026-10-12 (PR #82, versión de desarrollo):** el robot de acciones **ya ejecuta operaciones mediante Chrome visible**, con autorización explícita de la tanda, verificación de la sesión/perfil, botones localizados de forma estricta y comprobación posterior. **Aún no está publicado como release estable ni probado contra la sesión real del propietario**. Una variación del DOM o un bloqueo de Instagram detiene el proceso: ninguna simulación equivale a aceptación real.

## Límites de producto

- **Mutuals** solo usa **Focos de revisión** (20/30/40); no tiene automatizaciones ni cambios de relación por robot. Para priorizar el Focus se añade la proporción Following/Followers *de cada perfil* solo cuando Profile Counts tiene ambas cifras con estado válido. Un cociente alto puede subir la prioridad de revisión, nunca autoriza unfollow ni implica fraude.
- **Automatizaciones** es un workspace separado con futuras tareas de cancelar solicitudes enviadas y dejar de seguir cuentas que no siguen de vuelta. Usa archivos y sesión visibles de Chrome local, no Meta Graph API; no solicita contraseñas de Instagram en la app.
- **Omitir esta vez:** excluye la entrada del lote de planificación actual; **Nueva tanda** limpia estas omisiones temporales.
- **★ Proteger / Favorito:** exclusión persistente por usuario de IG Cleaner e Instagram seleccionado, accesible desde **Perfiles protegidos**. Unfollow aprovecha también el set existente de protegidos de Review y Mutuals; los protegidos nunca deben ejecutarse.
- **Tiempos:** tamaño de tanda, descanso opcional entre tandas (incluido 0 minutos para desactivarlo) y espera mínima entre perfiles; ajustes por perfil y tarea. El backend persiste un registro de visitas para que una pausa/reinicio no restablezca límites.
- **Ejecución real desde Windows:** descargar un paquete de robot que incluya este PR (un ZIP antiguo v120.42 NO incluye el motor de acciones), extraer, abrir `Start-Insta-Cleaner-Robot.cmd`, iniciar sesión en la ventana de Chrome del robot, seleccionar el `@Instagram` correcto en Insta Cleaner, importar exportaciones completas cuando se trate de unfollow, entrar a Automatizaciones, escoger la tarea, configurar tamaño/descansos, revisar favoritos, pulsar **Ejecutar tanda seleccionada** y confirmar la lista; usar **Pausar/Reanudar** cuando se necesite.
- **Confirmación y validación:** cada clic requiere estado visible previo (Following / Requested) y una señal visible posterior (Follow). Si el perfil te sigue visiblemente, el modo unfollow lo manda a revisión en vez de cambiar la relación. Ante login/challenge, navegación a otro perfil, botones ambiguos o estado final desconocido, **detener y marcar para revisión**.
- **Auditoría:** los resultados y registros de ritmo son locales, segregados mediante hash por login de Insta Cleaner, Instagram y tipo de acción. Los éxitos no se repiten al reanudar. Una acción de resultado ambiguo no se repite automáticamente.
- **Protegidos en vivo:** al iniciar una tanda se envían todos los protegidos al controlador local; mientras el robot trabaja solo se permite **añadir** protecciones para no quitar una defensa por una carrera de estado. Una tanda nueva toma la lista actual de favoritos, incluidos los retirados deliberadamente.

## Requisitos antes de activar acciones reales

1. Cola explícita verificada a partir del Instagram seleccionado; no asumir que la ausencia en un archivo parcial demuestra falta de followback.
2. Confirmación de usuario por tipo, conteo y perfiles antes de comenzar la primera tanda; deduplicación e idempotencia por cuenta y tipo de acción.
3. Verificación del nombre visible y del estado del botón **en el perfil actual** antes de cambiar una relación; nada de clics ciegos ni botones por posición fija.
4. Ante desafíos, CAPTCHA, login, cambio de cuenta, ausencia de controles, cancelación, límite de plataforma o error, **detener**, mostrar causa y conservar avance; no eludir restricciones ni reintentar agresivamente.
5. Pausar y Reanudar deben guardar registros auditables por perfil: pendiente / ejecutado / omitido / protegido / fallido, con fecha y método. No tomar un clic como éxito sin verificar estado posterior.
6. Respeto estricto a la misma identidad del app-login e Instagram, sin cambios de cuenta tácitos, ni reutilizar acciones en otra sesión.
7. Pruebas unitarias con DOM sintético, navegador real con cuentas controladas (incluida confirmación y desafío), pruebas de controles en compact/desktop, regresión de Focus y protección persistente.
8. Publicar solo después de CI verde y autorización de release. Probar en cuenta real puede provocar límites de Instagram; no hay garantía de disponibilidad.

Los exports y resultados siguen siendo locales. No se debe enviar la contraseña de Instagram ni cookies a Supabase.

## Límites de verificación actual

La prueba automatizada usa un navegador simulado (botones `Following`, `Requested`, `Unfollow`, `Cancel Request` y `Follow`) más verificaciones de cuenta, protección y confirmación. **No** se ha demostrado todavía que los botones reales de Instagram en el equipo de la persona tengan exactamente esos roles/nombres ni que los resultados funcionen con cuentas privadas e internacionalización diversa. El robot no intenta resolver CAPTCHA ni evadir restricciones. Antes de usarlo con muchas cuentas, validar con una tanda pequeña y revisar su historial.

### Flujo de Unfollow público y privado — 2026-10-12

La pantalla puede mostrar **Siguiendo/Following** y abrir un **menú** que contiene **Dejar de seguir/Unfollow**. En un perfil **público** ese segundo clic puede producir directamente el botón **Seguir/Follow**; no se debe exigir una confirmación inexistente. En un perfil **privado** puede aparecer después un diálogo adicional **Dejar de seguir/Unfollow/Confirmar**, que se confirma únicamente si efectivamente está visible y el perfil sigue siendo el indicado. Si no hay menú, el robot comprueba si el botón final ya cambió; si no hay estado verificable se detiene con revisión manual. Nunca da éxito por el clic solamente. Las pruebas simulan ambos caminos en inglés y español; falta aceptación con sesión real.
