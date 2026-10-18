### Development candidate — 2026-10-18: five target tabs with retained verification

- The owner requested 5 Chrome **tabs** (not separate browser windows) and tab closure only after a confirmed result. The candidate action controller uses up to five target-page slots. An `ok` (actual visible Follow/Follow Back after owner verification) can close its tab, as can an explicitly pre-click skipped profile; missing controls, uncertain results and post-click verification failure retain their tab for human review. If five cannot be confirmed, no sixth relationship action starts.
- The robot stays with **sequential** relationship-changing clicks, existing visit cooldown/journal, account ownership and protections; five tabs do not mean five simultaneous unfollows. Bounded UI waits address possible loading races without claiming that Instagram's current layout is known or automatically bypassing challenges.
- Pause warns when retained tabs will be closed; journal status remains authoritative, and uncertain clicks are never auto-replayed.
- This is development code only until current-commit CI and owner Windows Chrome tests pass; do not advertise it as in the public v120.50 installer.

# Automatizaciones — especificación y estado

**Estado 2026-10-12 (PR #82, versión de desarrollo):** el robot de acciones **ya ejecuta operaciones mediante Chrome visible**, con autorización explícita de la tanda, verificación de la sesión/perfil, botones localizados de forma estricta y comprobación posterior. **Aún no está publicado como release estable ni probado contra la sesión real del propietario**. Una variación del DOM o un bloqueo de Instagram detiene el proceso: ninguna simulación equivale a aceptación real.

## Límites de producto

- **Mutuals** solo usa **Focos de revisión** (20/30/40); no tiene automatizaciones ni cambios de relación por robot. Para priorizar el Focus se añade la proporción Following/Followers *de cada perfil* solo cuando Profile Counts tiene ambas cifras con estado válido. Un cociente alto puede subir la prioridad de revisión, nunca autoriza unfollow ni implica fraude.
- **Automatizaciones** es un workspace separado con futuras tareas de cancelar solicitudes enviadas y dejar de seguir cuentas que no siguen de vuelta. Usa archivos y sesión visibles de Chrome local, no Meta Graph API; no solicita contraseñas de Instagram en la app.
- **Omitir esta vez:** excluye la entrada del lote de planificación actual; **Nueva tanda** limpia estas omisiones temporales.
- **★ Proteger / Favorito:** exclusión persistente por usuario de IG Cleaner e Instagram seleccionado, accesible desde **Perfiles protegidos**. Unfollow aprovecha también el set existente de protegidos de Review y Mutuals; los protegidos nunca deben ejecutarse.
- **Tiempos:** tamaño de tanda, descanso opcional entre tandas (incluido 0 minutos para desactivarlo) y espera mínima entre perfiles; ajustes por perfil y tarea. El backend persiste un registro de visitas para que una pausa/reinicio no restablezca límites.
- **Ejecución real desde Windows:** descargar un paquete de robot que incluya este PR (un ZIP antiguo v120.42 NO incluye el motor de acciones), extraer, abrir `InstaCleanerPro.exe` (sin `.cmd` separado), iniciar sesión en la ventana de Chrome del robot, seleccionar el `@Instagram` correcto en Insta Cleaner, importar exportaciones completas cuando se trate de unfollow, entrar a Automatizaciones, escoger la tarea, configurar tamaño/descansos, revisar favoritos, pulsar **Ejecutar tanda seleccionada** y confirmar la lista; usar **Pausar/Reanudar** cuando se necesite.
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

### Solicitudes enviadas aún pendientes — evidencia visual 2026-10-12

El usuario confirmó con capturas reales de Instagram web que el perfil privado con botón **Requested** puede mostrar al pulsarlo un diálogo con el aviso **“If you change your mind, you'll have to request to follow @usuario again.”**, la acción roja **Unfollow** y la alternativa **Cancel**. En este estado **Unfollow significa retirar/cancelar la solicitud de seguimiento**, mientras que **Cancel** cierra el diálogo sin cambiarla. No se debe elegir la acción solo por el texto «Unfollow»: el robot exige además haber comprobado **Requested**, que el aviso del diálogo mencione solicitar seguimiento **de nuevo** y que contenga el **@usuario exacto** del perfil abierto. Solo entonces pulsa Unfollow y comprueba que aparezca Follow/Seguir. La alternativa Cancel jamás debe confundirse con «Cancelar solicitud». Sigue aceptando el flujo explícito Cancel Request/Cancelar solicitud cuando Instagram use ese texto. Se agregan tests con Chromium auténtico usando HTML simulado tanto en inglés como español, incluidos perfiles protegidos, nombres que no coinciden y avisos ambiguos. La prueba real con una sesión iniciada queda pendiente y no se realiza en CI.

### Verificación final Follow vs. Follow Back — evidencia de dos videos (2026-10-12)

Los videos enviados por el propietario muestran dos estados finales distintos tras una acción manual en Instagram web: **Follow Back** en una cuenta que sí sigue al propietario cuando este deja de seguirla; **Follow** cuando se cancela una solicitud aún pendiente y en cuentas que no siguen al propietario. Ambos demuestran ausencia del seguimiento saliente pero **no** expresan la misma relación entrante. El robot conserva el resultado `ok` para ambos si el estado final aparece en el encabezado correcto, con un mensaje de auditoría diferente indicando si todavía te sigue. La tarea automática **No me siguen** sigue teniendo el filtro conservador que bloquea actuar si el perfil muestra explícitamente `Follows you/Te sigue`; la ilustración manual de un caso mutuo no autoriza eliminar mutuals automáticamente. 

La advertencia del modal de cancelación puede escribir `@usuario.` con un punto final de oración. El comparador de @handle ahora acepta esa puntuación, pero rechaza extensiones `@usuario.otro` o `@usuario2`. Pruebas Chromium actualizadas para estado `Follow Back` y esos límites.

### Resumen interactivo de incidencias — 2026-10-12

**Al finalizar una tanda** o durante la recopilación, la sección Automatizaciones muestra un resumen independiente de anomalías, con filtros `Sin revisar/Todos/Revisados` y por clase de incidencia, búsqueda de @usuario, enlaces **Abrir perfil**, acción **★ Proteger** y **✓ Ya revisé** (reversible). Las revisiones del usuario se guardan en almacenamiento local por cuenta de IG Cleaner, cuenta Instagram, tarea e identidad de la incidencia (username + tipo + fecha); la misma anomalía en otra fecha no queda ocultada por una decisión vieja. El resumen de cada tarea se almacena por separado localmente y se puede consultar al regresar a esa cuenta, incluso tras recargar la página.

Los códigos de incidencias reportan: `unexpected_followback` (en `No me siguen` aparece Follow Back después de la acción), `pending_already_following` (estaba en el export Pending pero ahora aparece Following/Siguiendo: **no se toca**), `pending_not_requested`, `mutual_before_action`, `missing_profile_info` y `requires_manual_review` (bloqueos, errores o estado final ambiguo). Un estado `review` previo al clic puede dejarse en la lista y continuar con otros perfiles; si pudo ejecutarse un clic ambiguo, el robot se detiene y **nunca reintenta a ciegas**. Las cuentas protegidas no se operan. El progreso distingue visitados/analizados, acciones correctas y perfiles aún sin visitar.

Se añadieron tests unitarios por cuenta y de navegador Chromium para Pending→Following/Siguiendo y falta de información sin clic, y un test Node para la lista filtrable, el enlace directo, la revisión persistente y la separación por cuentas. **La prueba con Instagram conectado en el equipo del propietario sigue pendiente**; no se ha publicado release.

## Integración Windows en una sola aplicación — 2026-10-12

La versión de desarrollo de Windows contiene **un solo ejecutable** `InstaCleanerPro.exe`, que incluye la interfaz de Insta Cleaner Pro y ejecuta el controlador local de Profile Counts y Automatizaciones **dentro del mismo proceso**. No requiere lanzar un `.cmd`, un servidor manual ni abrir un HTML independiente. Al hacer doble clic abre la app en una ventana dedicada de Chrome en modo aplicación; al iniciar una tarea, el robot utiliza otra ventana visible de Chrome para tu sesión de Instagram, donde las contraseñas se introducen únicamente en Instagram. Las decisiones y controles de ejecución permanecen en la interfaz de Insta Cleaner.

El ejecutable copia únicamente el HTML incorporado a una **ruta persistente** en `%LOCALAPPDATA%\Michels Lab\Insta Cleaner Pro\IG-Cleaner-Pro.html` y mantiene su perfil de trabajo en `workspace-browser` para conservar origen/storage entre actualizaciones. Los datos previos del robot de `%USERPROFILE%\.ig-cleaner-pro\` se reutilizan. **Los datos guardados en un HTML anterior abierto desde otro navegador/ruta no se migran solos**; hay que usar la exportación/importación de respaldos existente. Cerrar la ventana solicita pausa y espera a que los trabajos terminen el punto seguro antes de apagar el controlador.

El ZIP PREVIEW se compila con PyInstaller (`--onefile --windowed`) y HTML/icono integrados; ya no distribuye `.cmd` ni un HTML que el usuario deba lanzar. `--healthcheck` y pruebas unitarias comprueban el contrato, pero sigue pendiente la instalación y aceptación de usuario real en Windows/Instagram. **Android no tiene este motor Playwright** y la paridad de automatizaciones no debe suponerse. Sin release estable ni integración de PR antes de validación completa.
