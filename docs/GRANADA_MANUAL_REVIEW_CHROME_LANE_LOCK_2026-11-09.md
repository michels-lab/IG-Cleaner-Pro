# Operación Granada — no abrir Review manual en un Chrome ocupado por otro robot

Fecha: 2026-11-09. Alcance: dos cuentas de Instagram, edición pública y Developer de InstaCleaner en Windows.

## Defecto

El botón de Review manual después de reiniciar Windows usa `ActionRobot.open_profile()` para lanzar Chrome con `--user-data-dir` del propietario y cuenta seleccionados. Antes verificaba únicamente el hilo local. Si otra instancia de InstaCleaner tenía un worker Playwright supervisando **esa misma sesión persistente**, la nueva app podía enviar `--new-tab` hacia el Chrome ya ocupado. Esto podía interferir con una tanda activa y volver confusa la asociación entre sesión y objetivo.

## Cambio

`open_profile()` ahora exige `ChromeLaneLease(session)` al emitir la navegación manual. Es el mismo candado OS y directorio exacto que retiene `ActionRobot._run_with_lease()` durante el robot. Cuando otra app posee ese Chrome, se deniega la apertura antes de llamar a `subprocess.Popen`. Para la segunda cuenta, cuyo Chrome está libre, la revisión permanece disponible. El candado se libera en `finally` implícito del context manager incluso si Chrome devuelve un error; no se mantiene abierto durante la inspección manual.

La operación sigue siendo navegación con confirmación explícita, sin Unfollow, Cancel Pending ni cambios de estado Reviewed/OK. Ningún registro WAL se modifica, y no se usa un perfil predeterminado ajeno.

## Pruebas

`tests/test_action_chrome_profiles.py` ejecuta los métodos productivos con Chrome simulado: instancia externa mantiene `ChromeLaneLease(A)`; abrir Review en A es denegado sin `Popen`, pero B sí abre el directorio B; liberar A permite abrirlo explícitamente. Otra prueba simula fallo `Popen` y comprueba que el bloqueo no queda retenido. Linux CI e instalador integrado Windows ya ejecutan este archivo.

## Puerta de liberación

Solo código y tests. Sigue prohibido release, RC, instalador público y APK hasta recibir el ZIP original y validación física de Unfollow y Cancel Pending en ambas sesiones Instagram.
