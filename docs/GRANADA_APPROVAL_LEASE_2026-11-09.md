# Operación Granada: bloqueo entre procesos antes de aprobar una tanda

Una edición pública o Developer de InstaCleaner puede usar el mismo WAL de acciones después de reiniciar Windows. La lectura y aprobación de tandas guardadas no debe depender exclusivamente de un RLock local.

`ActionRobot.approve_batch` exige el mismo bloqueo OS global+owner/account usado por los robots, relee el lote y el historial de clics bajo ese bloqueo, conserva resultados de posibles clics para revisión y siempre libera el bloqueo. La edición que encuentre otro robot activo falla sin modificar los datos.

`tests/test_action_batch_approval_lease.py` verifica dos cuentas, ámbitos incorrectos, bloqueo externo y conservación exacta de las evidencias. CI Linux y Windows ejecutan la prueba. Cambios en fuente solamente, sin operaciones Instagram ni publicación de instaladores. Reemplaza el PR #336 histórico cuya rama divergió.
