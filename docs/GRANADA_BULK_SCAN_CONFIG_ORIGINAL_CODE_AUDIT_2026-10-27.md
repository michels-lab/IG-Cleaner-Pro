# Operación Granada — auditoría del código original y ajustes configurables de lectura masiva (2026-10-27)

## Evidencia recuperada, no necesita reenviar el archivo original

Se recuperó el archivo que el usuario compartió: `Pasted text(3).txt`, paquete JavaScript/React/Webpack minificado de aproximadamente 149 KB. Se leyó su estructura de constantes, formulario de configuración y controlador de búsqueda. **No se copió ni se incorporó el bundle**; se usaron sus principios técnicos para una implementación independiente y mantenible.

Hallazgos del código de referencia:

- Existe un menú de **Timings/Settings** que permite cambiar y **guardar** cinco parámetros: tiempo entre ciclos de búsqueda, descanso después de varios ciclos, pausa entre unfollows, descanso después de múltiples unfollows y cantidad de usuarios por ciclo. Se mantiene una clave de almacenamiento de preferencias `iu_timings`. InstaCleaner no debe mezclar las pausas de lista con los tiempos de acciones mutadoras.
- El ejemplo alterna ciclos breves y descansos extendidos, incorpora pequeñas variaciones en algunos tiempos y muestra avisos de pausa y de `feedback_required`. La constante de búsqueda larga `CHECKS_BEFORE_LONG_SLEEP` tiene valor 15 en esa versión. También hay un mecanismo de reintentos en peticiones temporales: **no se copió ese comportamiento**, porque un bloqueo de Instagram en la aplicación nueva debe suspender nuevos GET y respetar `Retry-After`.
- El ejemplo posee límites de cursor/página y distingue la carga de seguidores de la comparación con seguidos, pero no ofrece garantía de completitud de las listas ni de política de Instagram. Para InstaCleaner es obligatorio probar que **ambas** colecciones terminaron sin cortes antes de presentar «no me sigue».
- El código de referencia también incluye funcionalidad de unfollow y otras dependencias ajenas al lector. **No se trasplantaron**.

## Problema observado en v120.70

El screenshot del usuario mostraba `Instagram protection: 2s rest after 12 bulk followers pages` y ningún botón de configuración de pausas. La causa verificable estaba en el código:

1. `tools/profile_lists_live.py` aplicaba constantes fijas (2500 ms, cada 5 páginas 12000 ms y cada 25 páginas 90000 ms) sin una interfaz de ajustes ni un registro por cuenta.
2. `tools/live_relationship_snapshot.py` mostraba `milliseconds // 1000`: convertía **2500 ms en "2s"**, aunque el trabajador esperase 2.5 segundos.
3. El bloque de `desktop/ig_cleaner_pro_v120_27_synced_companion.html` solo tenía **Verify**, **Stop** y **Last snapshot**. Los controles «batch size», «rest between batches» y «delay between profiles» que aparecen después del bloque corresponden al robot de acciones por perfiles, no a la consulta masiva.

## Implementación propia

- Nuevo contrato `tools/live_scan_settings.py` con **Recomendado (predeterminado)**, **Más pausado** y **Personalizado**. Persistencia atómica segregada por usuario de la app y workspace de Instagram; `/api/actions/live-settings` valida y devuelve el perfil real del motor y no toca la sesión de Instagram.
- Recomendado: hasta 200 cuentas solicitadas por página, 2.5 s entre páginas, 12 s cada 5 páginas, 90 s cada 25 y 15 min de intervalo entre escaneos completos. Más pausado: 100 cuentas solicitadas, 5 s base, 25 s cada 5, 180 s cada 20 y 30 min entre escaneos.
- Personalizado **no puede debilitar** los valores mínimos del modo Recomendado: entre 25 y 200 miembros solicitados por página, espera de 2.5–30 s, descanso corto de 12–180 s cada 2–5 páginas, largo de 90–600 s cada 10–25 páginas, y 15–180 min para repetir. Las pausas frecuentes aumentan la duración; estas cifras **no son límites oficiales de Instagram**.
- Los controles aparecen dentro de un panel de ajustes dedicado, con recomendación descriptiva, valores visibles, advertencia de riesgo, botón **Guardar y aplicar** y opción **Restaurar recomendado**. Los presets usan valores certificados por el backend; ningún control solo visual sustituye al servidor.
- Las opciones seleccionadas se cargan al iniciar el scan y se mantienen inmutables durante esa ejecución. No se puede guardar cambios mientras el scan esté activo. El estado informa páginas JSON y miembros únicos reales. La duración muestra `2.5s`, no `2s`.
- No se puede quitar el freno obligatorio ante HTTP 429/403/503 o `feedback_required`, ni el enfriamiento conservador de al menos 30 minutos con respeto de `Retry-After`, compartido por la sesión local de Chrome. Nunca se reintenta automáticamente un bloqueo, se cambia de IP ni se navega perfil por perfil para obtener estas listas.
- Los ajustes no modifican Unfollow, Cancel Pending, registros de click WAL, importación ZIP, cuentas protegidas, otras automatizaciones o Android. La disponibilidad del endpoint privado de Instagram sigue requiriendo prueba real del usuario.

## QA y publicación

Pruebas nuevas: presets, límites, intentos de manipular valores, persistencia entre procesos, aislamiento por cuenta, bloqueo de edición durante lectura, lectura de valores por el trabajador y contrato UI↔backend. Exigir pruebas exact-head de Desktop, Windows real normal/Developer instalado y Android. Esta modificación es **source-only** hasta una siguiente release FINAL normal; no alterar los 12 archivos de la v120.70 ya publicada.

El usuario puede compartir una nueva versión de su archivo de referencia más adelante, pero la presente revisión se basa en el que **ya había proporcionado**.
