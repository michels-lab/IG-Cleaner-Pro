# Granada P0 — WARNING por perfil; la tanda continúa

**Cambio solicitado:** una irregularidad aislada de un @usuario NO debe detener toda la tanda de Instagram. El caso real fue Cancel Pending mostrando el diálogo normal «¿Dejar de seguir a __cesarin_?» después de varias cancelaciones correctas.

## Contrato del worker
- Una fila problemática queda **Review/Warning**, con @usuario, motivo, hora, estado y fases de `click_intent` originales en el **mismo journal canónico**. No se convierte en OK, no se vuelve a pulsar y no se elimina el historial.
- Después de fsync/atomic-rename del resultado, el worker comprueba **de nuevo** que existe una sesión sana y que el owner verificado sigue siendo el mismo, sin CAPTCHA, challenge, contraseña ni otra identidad visible.
- Si es una anomalía del **perfil individual**, el worker puede cerrar esa pestaña (nunca una confirmación de relación), dejando la fila Review y acceso a «Revisar perfiles» read-only, y continuar al siguiente perfil distinto con el pacing configurado.
- Se aplica a Cancel Pending con `result=review`, incluido `pending_wrong_relationship_dialog`, y a Unfollow con intención potencial ya persistida (el comportamiento previamente conocido). Los resultados sin clic se conservan como Review y se saltan sin frenar la tanda.
- **No continúa** por una falla global: owner incorrecto/no verificado, login perdido, challenge de seguridad, límite identificado como bloqueo, `result=blocked`, pérdida de integridad del WAL, error al cerrar la pestaña o cancelación/pausa solicitada.
- Ningún proceso reinicia automáticamente un perfil con Review tras reinicio: `_saved_journal_blocks_action` mantiene el resultado intentado como no reutilizable. No se requiere que el usuario revise cada Warning antes de poder continuar el trabajo restante en esa misma sesión sana.

## Validación
- `tests/test_cancel_request_unfollow_dialog_safety.py`: HTML en Chromium real (offline) para caso español/inglés y la carrera Requested→Following. Nunca pulsa el rojo «Dejar de seguir».
- `tests/test_cancel_warning_continues_batch.py`: ejecuta la **lógica real de `ActionRobot._run`** con Chrome falso y fases WAL originales: primer perfil queda Review sin segunda confirmación, el segundo y tercero completan, el journal no permite replay, el estado final es Partial. Un owner no verificable impide continuar al segundo perfil. Reiniciar un batch con mismas filas no reintenta ninguna.
- General CI, Profile Counts y Windows Setup son bloqueantes. No hacer release hasta la comprobación del SHA exacto y aceptación en instalación Windows real.

**Nota importante:** la interfaz actual de Windows en ejecución no se modifica automáticamente por un PR. Los límites y restricciones de Instagram no pueden ser anulados por el robot.
