# GRANADA — dos sesiones de acciones visibles en Windows

**Fecha:** 2026-10-30. **Estado:** cambio fuente en rama, pendiente CI y revisión. **Release:** congelado.

## Necesidad

El backend de PR #286 ya ofrece dos robots de acción con sesiones persistentes Chrome exclusivas por workspace, pero el usuario no puede utilizar ni inspeccionar sus endpoints desde la interfaz Windows. La interfaz debe distinguir claramente "la cuenta que está siendo revisada" y evitar botones duplicados o cualquier falso anuncio de mutaciones paralelas.

## Entrega

- Nuevo panel oscuro `tools/dual_action_windows_ui.py`: aparece inmediatamente después del **Automation Command Center** existente; dos tarjetas en diseño responsivo, con cuenta/@handle/estado/activos/cantidad revisada y problemas.
- Botones **Vincular dos cuentas** (selector superior, confirmación explícita de los dos @handles y de que solo habrá un motor activo), **Actualizar estado**, **Revisar pendientes** por cuenta/tarea, **Abrir revisión** por @usuario persistido de la cohorte y **Pausar esta cuenta**.
- El panel **no** tiene botón que auto-inicie Unfollow o Cancel. Las tandas siguen requiriendo los controles y confirmaciones existentes del producto: no se trata de "dos unfollows paralelos completados" ni se reejecuta un target de Review.
- Todas las operaciones se envían al puente local usando la capacidad de la propia ventana Windows (`#igc-robot=port.token`), sin mostrarla, copiarla o guardarla en logs. Identidad y lista de cuentas provenientes de `IGC_INSTAGRAM_PROFILES` y su registro vigente; se envían owner/account/task y confirmaciones específicas por acción. No se fabrican sesiones.
- `tools/ig_cleaner_desktop.py`: inserción del panel en la **copia local de HTML** de Windows, no en el HTML original de web/Android ni Developer Edition. Solo con `</body>` exacto, inserción atómica, y vuelve a comprobar hash antes de sobrescribir. No toca datos de usuario ni vuelve a importar ZIP.
- Pruebas Python sin red para garantizar idempotencia, integridad de origen, Developer sin overlay, fail-closed HTML malformado, controles de consentimiento y ausencia de auto-unfollow.
- El panel se monta mediante `MutationObserver` incluso si el usuario navega de Home a Automatizaciones después de los primeros 7.5 segundos; prueba Chromium con incorporación tardía del Command Center, sin refrescar sesión ni abrir Chrome adicional.
- Prueba Chromium de **la interfaz renderizada** `tests/dual-action-windows-panel-browser.test.cjs`: comprueba par de cuentas, contrato de token/confirmación de vinculación, Pending seleccionado por cuenta, reapertura sin clic, stop de la cuenta correcta y prohibición de start-one implícito.
- CI general + instalador Windows tienen nuevos checks obligatorios, y paths añadidos a la política del instalador Windows.

## Bloque adicional: continuar exactamente la tanda guardada

- Botón `Continuar tanda guardada` en cada tarjeta. **No se activa con una lista nueva**: antes exige cargar mediante `review-one` el registro `batch_id` y los objetivos originales guardados en el journal canónico de esa cuenta.
- Se muestra una confirmación con @handle, tipo de acción, número de objetivos y conteo de entradas todavía pendientes; no se cambian ni reordenan nombres. Un lote sin objetivos vírgenes se bloquea y exige revisión manual.
- Para `unfollow` hay un segundo consentimiento explícito del propietario sobre su lista completa de seguidores. **Esta confirmación es una declaración del propietario, no una verificación automática de que el ZIP/consulta live esté completo**; la validación de perfiles y todas las barreras de WAL, visitados/protegidos, owner, Chrome exclusivo y anti-replay permanecen a cargo de `ActionRobot.start`.
- El payload contiene `owner/account/expected_handle/task/targets/batch_id` originales, tamaño de tanda y pausas desde los controles configurables existentes, más confirmaciones `task:N` y `action-workspace-start:owner:account:task`. El endpoint `start-one` **no permite otra mutación simultánea**.
- La prueba Chromium demuestra que Review/Open/Pause nunca disparan `start-one`; solo el botón explícito lo hace, preservando toda la cohorte original y con el token exacto de la ventana.
- Una segunda operación explícita **Aprobar revisión** usa el método canónico `ActionRobot.approve_batch` tras verificar propietario, cuenta, tarea y `batch_id`; requiere que no existan perfiles sin observar y que todos los robots de mutación estén pausados. No convierte ni oculta un clic incierto: queda en `unresolved_usernames` amarillo y se conserva el journal completo.
- Resultados de cohorte renderizados en dos tarjetas con **verde OK, amarillo Review, gris No disponible** y el timestamp `at` del registro real. Los resultados verdes no aparecen en el selector de reapertura de Review. Sin fecha histórica, se indica `sin fecha registrada`, nunca se inventa una hora.

## Límites y siguientes tareas

- No se habilitaron dos mutaciones paralelas: el WAL global heredado permanece activo. La apertura de Review es navegación manual, no ejecución del clic.
- La opción de **continuar una tanda original guardada** está conectada al controlador correcto. Iniciar tandas completamente nuevas desde la selección principal de la UI todavía usa el controlador clásico y debe migrarse con garantías de identidad y equivalencia funcional; no se duplica la selección ni se autorizan clicks por delegación implícita.
- El panel usa únicamente la app instalada Windows; las páginas web/Android mantienen su diseño y funcionalidad actual.
- La aceptabilidad real requiere probar dos sesiones Chrome firmadas con sus owners correctos en el Windows del propietario y resolver issues #164 y #176 antes de cualquier release.

**No fusionar ni publicar hasta que CI y Windows Chromium del SHA exacto hayan terminado en verde.**
