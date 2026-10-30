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
- Prueba Chromium de **la interfaz renderizada** `tests/dual-action-windows-panel-browser.test.cjs`: comprueba par de cuentas, contrato de token/confirmación de vinculación, Pending seleccionado por cuenta, reapertura sin clic, stop de la cuenta correcta y prohibición de start-one implícito.
- CI general + instalador Windows tienen nuevos checks obligatorios, y paths añadidos a la política del instalador Windows.

## Límites y siguientes tareas

- No se habilitaron dos mutaciones paralelas: el WAL global heredado permanece activo. La apertura de Review es navegación manual, no ejecución del clic.
- Hace falta conectar el formulario de **Run/Continue** al controlador nuevo por cuenta conservando las preferencias, revisiones y aprobaciones originales. Esta versión evita duplicar el formulario, pero aún no sustituye el motor clásico visible.
- El panel usa únicamente la app instalada Windows; las páginas web/Android mantienen su diseño y funcionalidad actual.
- La aceptabilidad real requiere probar dos sesiones Chrome firmadas con sus owners correctos en el Windows del propietario y resolver issues #164 y #176 antes de cualquier release.

**No fusionar ni publicar hasta que CI y Windows Chromium del SHA exacto hayan terminado en verde.**
