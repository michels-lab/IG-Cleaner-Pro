# Operación Granada — dos robots reales simultáneos con autorización explícita

**2026-10-30. Estado: código nuevo en PR, SIN release ni aceptación física.**

## Cambio funcional

El supervisor Windows `DualActionWorkspaces` usa por defecto `ScopedActionLease`, por lo que sólo admite **un trabajo de mutación a la vez**. El propietario puede activar expresamente **Dos robots de acciones simultáneos** al vincular sus dos workspaces de Instagram, que deben tener dos @handles, dos `account_key` y dos perfiles persistentes Chrome diferentes. Sólo si hay `read_only_consent:true`, `parallel_actions_consent:true`, `acknowledge_parallel_actions:true`, `acknowledge_serial_actions:false` y la confirmación exacta `dual-action-workspaces-parallel:<accountA>:<accountB>` se crea `SharedGlobalActionCohort` de producción.

`ActionRobot` NO se reemplaza. Cada instancia lleva su propia carpeta Chrome, `worker/stop_event/current/targets` y archivos `instagram-actions-<hash(owner/account/task)>.json`, visitas, listas protegidas y cohortes pendientes. Ambas instancias del mismo dueño toman un **lease por scope** dentro de un único bloqueo OS heredado. Este permanece ocupado desde que arranca el primero hasta que termina el último robot, incluso si A acaba antes que B. Un InstaCleaner antiguo (Public o Developer) no puede empezar un mutador en paralelo porque intenta tomar el **mismo bloqueo global**; un tercer scope o un propietario diferente tampoco puede reclamar el coordinador.

## Consentimiento y control en la app

- Checkbox explícito (desmarcado por defecto) y diálogo independiente de confirmación al cambiar de modo. No se cambia el modo con workers activos.
- Cada nueva tanda / continuación guardada exige `owner/account/expected_handle/task/targets`, la confirmación existente `action-workspace-start` y **otra** `parallel-action-workspace-start:<owner>:<account>:<task>` cuando el modo paralelo está activo. Un consent de Cancel Pending no autoriza Unfollow.
- `start-one` sigue delegando en `ActionRobot.start`: valida identidad exacta al abrir su propia sesión Chrome, relación actual visible, journal, intención de clic antes de la mutación, lista protegida y coherencia de tandas. Si la plataforma muestra un challenge o la relación queda incierta, el robot debe conservar el evento como Review/Pending, no repetirlo ni afirmar éxito.
- La tarjeta A puede pausarse sin pausar la tarjeta B; `status` devuelve el modo confirmado por servidor, no una inferencia de la casilla. Ambos controladores siguen protegidos con el token local existente del puente Windows.
- El preflight local de una tanda nueva en B puede ejecutarse mientras A está activo, porque consulta únicamente el journal B. Una tanda nueva no se prevalidará contra un journal A que está siendo modificado en ese momento.
- **Los límites de Instagram son externos y no se pueden garantizar.** Los dos workspaces necesitan pacing independiente, observación de challenge y pausas manuales; no se prometen volúmenes ni períodos sin bloqueos.

## Pruebas obligatorias

Se instancian los supervisores **de producción reales** con `offline_test_runner=None` y consentimiento paralelo. Sólo se sustituye el cuerpo `_run` que normalmente ejecutaría Playwright; los métodos `start`, WAL, reserva OS compartida, ChromeLaneLease, validación de owner, autorización y pausas se ejecutan reales en la prueba. Casos: serial por defecto, consent falsos y handles cruzados, consentimiento adicional por cuenta/tarea, dos workers con UN lease global heredado, detener A y conservar B, protección B con A vivo, ventana Chrome B ocupada, preflight B mientras A activo, prohibición de reconfigurar en marcha y puente Windows inicial serial.

La suite Chromium prueba la casilla, confirmación de modo, modo devuelto por servidor, Unfollow A y Cancel Pending B con dos confirmaciones diferentes, token local y pausa exclusivamente A. Las mismas pruebas corren en CI general, Profile Counts y Windows Setup.

## Condiciones de salida

**No publicar release todavía**. Falta aceptación física de dos cuentas reales Chrome simultáneas y comprobación de comportamiento de Instagram con interrupciones, challenge, suspensión, reanudación y resultados inciertos. Cualquier fallo debe bloquear la publicación de versiones. La versión estable permanece igual y #164/#176 siguen abiertos hasta aceptación completa.
