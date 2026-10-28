# GRANADA — dos lanes de Chrome, exclusión real y Stop sin estados falsos

Fecha: 2026-10-27. Bloque **source-only**, rama `granada/dual-lane-lease-failclosed-20261027`.

## Hallazgo y alcance

`tools/dual_robot_lanes.py` ya inicia dos robots Chrome independientes para verificar en pantalla la cuenta de Instagram de cada workspace, pero ambos son **SOLO LECTURA / SUPERVISIÓN DE IDENTIDAD**. No habilitar mutaciones simultáneas. Actualmente `ActionRobot`, Cancel Pending y el WAL conservan el cierre exclusivo existente.

Se detectaron tres riesgos concretos de operación:

1. El control previo `self.lock` es local al proceso. Dos instancias de InstaCleaner podrían intentar ejecutar el supervisor sobre el MISMO directorio persistente de Chrome al mismo tiempo. La exclusividad nativa de Chromium puede rechazarlo, pero no debemos depender de un Chrome ya iniciado que redirige ventanas silenciosamente.
2. La API de Stop podía conservar temporalmente `verified: true` mientras el hilo aún terminaba; una devolución tardía del navegador podía restaurar el estado de verificación.
3. Un error de Playwright se devolvía como `str(exc)`, que puede contener rutas/URLs o identificadores no destinados a la UI.

## Solución implementada en rama aislada

- `tools/chrome_lane_interlock.py`: lock de sistema operativo no bloqueante, derivado del **directorio canónico de Chrome por owner/workspace**, en directorio de leases externo al perfil y fuera de exportaciones. Windows usa `msvcrt.locking`; POSIX `fcntl.flock`. El lock se mantiene durante **toda la vida** de la tarea y se libera por `finally` / cierre de fd, incluso ante crash de proceso.
- `DualRobotLanes._run_guarded` adquiere este lease antes de iniciar Playwright. Otra instancia que intenta usar el mismo Chrome queda `blocked` **sin ejecutar runner ni acciones**. Dos perfiles diferentes pueden trabajar a la vez; no se reutiliza el Chrome compartido del robot mutador.
- `stop_one`, `stop_pair` y `shutdown` invalidan `verified` inmediatamente y marcan `stopping`. Una devolución tardía del navegador no puede publicar `verified`; al terminar se cierra como `stopped`.
- Las fallas de Chromium se muestran por clase de excepción, sin insertar texto libre del error que pueda revelar rutas, URLs, tokens o configuración privada.
- `tests/test_dual_robot_lanes.py`: nuevas regresiones de colisión entre instancias, liberación del lock, stop tardío y ocultamiento de errores.

## Alcance y límites

No se editan sesiones, cookies, historial, ZIP, acciones, WAL, configuraciones de Instagram ni binarios. Las ventanas de **Chrome manual** ya abiertas pueden seguir manteniendo un lock nativo de Chrome; se debe cerrarlas antes de pedir al supervisor Playwright abrir el mismo perfil. Este cambio no intenta hacerse dueño de un navegador manual ni sortear bloqueos, desafíos o restricciones de Instagram. No prueba que las sesiones A/B del propietario realmente estén logueadas.

## Gates y punto de reentrada

- Estado inicial: código incorporado a una rama y pruebas escritas; **no se declara CI verde hasta comprobar el SHA exacto de la rama**.
- Validar pruebas Python `tests/test_dual_robot_lanes.py`, Desktop Chromium, `profile-counts-windows-preview` con Windows Setup instalado, Developer, seguridad de acciones, pruebas de Android que sean exigidas por el flujo y QA visual cuando corresponda.
- Si la CI falla: corregir en esta rama y volver a ejecutar; no merge a ciegas. No publicar nuevos releases: sigue vigente veto explícito del propietario hasta aceptación completa.
- PENDIENTES P0 independientes: dos verdaderos robots mutadores separados con WAL por cuenta y validación de identidad de cada acción; prueba física Unfollow, Cancel Pending y lectura completa de Followers/Following; recuperación de login/challenge. Issue #176 y #164 siguen abiertos.
