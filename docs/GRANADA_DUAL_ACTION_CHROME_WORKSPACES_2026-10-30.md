# Operación Granada — Dos workspaces Chrome para acciones (Windows)

**Fecha:** 2026-10-30 · **Estado:** cambios de fuente en PR; no release ni aceptación física.

## Problema real

El sistema de dos Chrome de supervisión ya reservaba dos `user-data-dir` aislados, pero el robot clásico de acciones `ActionRobot` seguía usando la sesión Chrome heredada del proceso. Eso impedía afirmar que Unfollow/Cancel estuvieran vinculados a la ventana correcta cuando el propietario cambiaba entre dos cuentas.

## Bloque implementado

- `tools/dual_action_workspaces.py`: **dos** instancias independientes de `ActionRobot`, cada una con su propio `session_dir` derivado de SHA256(owner+workspace) por `DualChromeSessions.directory`, distinto del Chrome clásico y del otro workspace. Las dos instancias comparten exclusivamente el **directorio canónico del journal y protecciones**, donde los registros ya están separados por owner/account/task.
- Controles locales protegidos por token: `POST /api/actions/dual-action-workspaces/configure`, `POST /api/actions/dual-action-workspaces/start-one`, `POST /api/actions/dual-action-workspaces/pause-one` y `GET /api/actions/dual-action-workspaces/status?owner=...`. El propietario configura explícitamente las dos cuentas; arrancar exige confirmación independiente de owner+workspace+task además de la confirmación del lote original. El motor sigue validando Followers completos, protegidos, no-replay, objetivos, WAL y sesión firmada antes de cada acción. Developer Edition **NO** puede invocar estos endpoints.
- `ActionRobot._run_with_lease` adquiere `ChromeLaneLease` del **mismo** directorio antes de iniciar Playwright. Un supervisor de identidad que posea ese Chrome bloquea la mutación: resultado `blocked`, sin clic y con la cohorte original conservada para inspección. Cada lock de Chrome se libera incluso con error o Stop.
- **Serialización expresamente preservada:** solo se permite un worker de acciones entre A, B y el motor heredado. También siguen funcionando `ScopedActionLease` y el bloqueo global de WAL entre Public y Developer, incluyendo instaladores anteriores. Ningún segundo Unfollow puede arrancar silenciosamente en paralelo.
- Al salir de Windows, se solicita parar **los dos** workers y se espera su cierre antes de terminar el proceso; no se abandonan hilos que pudieran hacer clic después de cerrar.
- Pruebas offline de cuenta exacta, consentimiento, errores de identidad, aislamiento de dos Chrome, exclusión cross-lane, bloqueo por supervisión, protegidos, Stop por cuenta, cierre ordenado, transport tokenized y rechazo de Developer. Gated en CI general, Profile Counts e instalador Windows.

## Lo que NO está completo

- No se han habilitado dos Unfollow simultáneos; esta funcionalidad requiere WAL concurrente seguro y compatibilidad de versiones instaladas, owner/target proof pre-click, recuperación de clic incierto y pruebas reales.
- La UI visible de Windows todavía debe vincular las dos tarjetas de acciones a estos endpoints; hoy se añadió un contrato backend probado, no se afirma que el usuario ya pueda pulsarlos en el instalador anterior.
- La nueva carpeta Chrome por cuenta puede requerir **inicio de sesión manual** independiente. No copiar cookies del perfil antiguo ni iniciar sesión automáticamente en otra cuenta.
- Manual review en cada Chrome, Batch OK/Review y experiencia de cancelación todavía deben integrarse en las tarjetas visibles.
- No se aceptan releases nuevos hasta completar la funcionalidad y la verificación física del propietario; #164 y #176 siguen abiertos.

## Próximos bloques

1. CI exact HEAD y pruebas Chromium/Windows Setup. Reparar las regresiones y fusionar solo con tests aprobados.
2. Integrar pestañas/tarjetas de automatización Windows para ver dos workspaces, botones de acción por cuenta, indicadores de identidad y revisión de cohorte, sin duplicar controles existentes.
3. Diseñar y probar WAL de dos escritores con migración fail-closed del mutex global; pruebas de crash y duplicado inter-cuenta e inter-proceso.
4. Validación física con dos sesiones Instagram y acciones de prueba aprobadas por el propietario, sin challenge bypass, y solo después completar release final conjunto Windows/Android.
