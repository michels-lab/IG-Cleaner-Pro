# GRANADA — inspección dual de tandas de acciones (solo lectura)

Fecha: 2026-10-27. **Sin publicar release.**

## Motivación

El propietario pidió que dos cuentas Instagram puedan funcionar en dos ventanas/robots independientes. Los dos supervisores Chrome de identidad y sus leases de sesión existen, pero el motor mutador `ActionRobot` conserva un cierre global del WAL y una sesión heredada. **No es seguro afirmar que dos robots Unfollow/Cancel corren en paralelo.**

Este bloque permite inspeccionar **dos tandas de acciones para dos workspaces distintos**, detectando casos que NO pueden reaparecer o contarse como OK antes de implementar un planificador paralelo con WAL seguro. No abre Instagram, no descarga listas, no navega perfiles y no realiza acciones.

## Capacidades implementadas

- Nuevo `tools/dual_action_preflight.py`: toma dos cuentas e identifica la tarea y los usernames exactamente seleccionados; valida el identificador de owner suministrado por la app y dos workspaces diferentes (el token del puente local autoriza la consulta, pero no sustituye una prueba fresca de login Instagram) y confirmación **específica de inspección**. Nunca acepta `audit` como mutación ni convierte esta confirmación en autorización para Unfollow.
- Consulta los archivos canónicos `instagram-actions-<scope>.json`, `-target-visits.json`, `-batch-reviews.json` y `action-protected-<scope>.json` del **mismo motor** actual. No crea otro historial donde una acción incierta pudiera desaparecer.
- Clasifica cada objetivo por prioridad: **protegido**, **acción con click incierto**, **previamente visitado/revisado**, **tanda sin aprobar**, o **sin evidencia de visita previa**. No reintroduce automáticamente los que fueron abiertos anteriormente aunque el clic no se confirmara. Una misma @cuenta en dos workspaces se mantiene segregada.
- Un journal malformado, evidencia desconocida o un robot de acción activo bloquean la inspección en lugar de calcular falsos elegibles. No se modifica ningún archivo histórico.
- Nuevo endpoint local protegido por token `POST /api/actions/dual-robots/preflight`. La respuesta está marcada `read_only_snapshot` con `actions_enabled=false` y `can_launch_parallel_unfollow=false`; cada lane lista las verificaciones aún ausentes (sesión exacta, relación actual, consentimiento de acción y WAL paralelo segregado).
- Pruebas offline `tests/test_dual_action_preflight.py` de aislamiento, protegidos, visita previa, intención de clic, tandas pendientes, historial corrupto, autenticación loopback y **cero escrituras**.
- CI Python y Windows integrado obligatorias para este módulo, incluso cuando solo cambien nuevos archivos del bloque.

## Estado y riesgos

**Implementado en rama de trabajo; no significa aceptado o fusionado.** El informe de elegibilidad es una fotografía local y NO garantiza que una relación de Instagram siga igual o que los dos logins Chrome sean correctos. No incluye UI nueva, no habilita dos mutaciones simultáneas. El endpoint se rechaza explícitamente en Developer Edition para no contaminar su aislamiento. La sesión real y la consistencia entre dos escritores requieren aceptar un journal/WAL por owner/account, bloqueo multi-proceso compatible con el robot heredado y pruebas de recuperación de clic desconocido antes de habilitarlo.

## Continuación obligatoria

1. Validar CI del SHA exacto; reparar fallos antes de fusionar.
2. Integrar panel visible de 2 tandas en Windows **sin duplicar los controles ya existentes** y exigir al backend el estado de cada cuenta.
3. Diseñar y probar la coexistencia de contratos globales heredados con nuevas exclusiones por cuenta, asegurar que los usuarios visitados no se repitan y que una acción incierta nunca se reprograme.
4. Habilitar acciones paralelas **solo** cuando el WAL, owner/target, Chrome sessions, protección, pausa, challenge, restart y aceptación física del propietario estén verificados.

Los issues #164 y #176 permanecen abiertos. El veto de nuevas versiones hasta completar aceptación real del producto se mantiene.
