# GRANADA P0 · Nueva tanda desde cada cuenta de Windows

**Fecha:** 2026-10-30 · **Estado:** desarrollo, sin release.

Antes, el panel Windows de dos cuentas sólo permitía consultar y continuar una cohorte guardada. Ahora cada tarjeta tiene una sección independiente **Nueva tanda · sólo esta cuenta** con entrada de @usuarios, tamaño de lote, segundos entre perfiles y descanso en minutos. No usa el perfil actualmente seleccionado para inferir la cuenta de destino: todos los comandos incluyen `owner/account/expected_handle` de la tarjeta vinculada.

## Pasos y garantías
1. El usuario pega 1–1,000 @usuarios; el parser rechaza identificadores inválidos, duplicados y listas vacías **sin eliminar ni reordenar** objetivos a escondidas.
2. **Verificar lista sin clics** llama `POST /api/actions/dual-action-workspaces/preflight-new-one` con el token local del host Windows y una confirmación de alcance exacto. El servidor consulta el `DualActionPreflight._inspect_one` existente y los **mismos archivos canónicos** de visitas, protecciones, journal y tandas del robot de acciones. No solicita Instagram, no abre Chrome, no crea una tanda y no da permiso de Unfollow.
3. La tarjeta muestra cada nombre con etiqueta NUEVO/BLOQUEADO y motivo (`protected`, `previously_inspected`, `uncertain_action` o `pending_cohort`). Si hay uno bloqueado, **no permite iniciar la lista completa**; tampoco filtra perfiles automáticamente.
4. El tamaño de tanda y el ritmo son **por tarjeta** (defaults conservadores 20 perfiles, 15 segundos, descanso 10 minutos; ajustables 1–1,000, 1–600 s y 0–240 min). Cambiarlos invalida la prevalidación anterior. Estos son ajustes operativos, **no una garantía de evitar límites de Instagram**.
5. **Iniciar tanda nueva** requiere un snapshot local previo y vuelve a consultar el estado canónico exacto para detectar cambios recientes. Tras verificar dueño, cuenta, tarea, lista inalterada y ritmos, pide confirmación visible. Unfollow pide **otra declaración explícita** del usuario sobre su lista completa y actual de seguidores. El preflight local no pretende probar que ya la tiene.
6. El endpoint existente `start-one` delega al `ActionRobot.start` original. El motor vuelve a comprobar historial, perfiles protegidos, login de la cuenta, relación actual, locks globales y Click WAL antes de toda acción. El botón se consume tras el intento para impedir doble ejecución accidental.
7. Todo esto sigue **serializado**: ningún robot puede ejecutar relaciones simultáneamente con el otro. No se publica release y no se toca Instagram real durante las pruebas.

## Pruebas
- Python: propietario/cuenta exactos; cambios de handle/tarea; historial previo, lista protegida, click incierto, cohorte pendiente, duplicados y permisos de Developer. Demuestra que el preflight no escribe ningún journal.
- Chromium real de Windows con puente simulado: bind, rechazo antes de verificar, duplicados, bloqueados, invalidación de lista y ajustes, dos consentimientos, envío exacto de la cohorte original a la cuenta seleccionada, segunda cuenta con Cancel Pending sin mezcla, estado local que cambia entre preflight e inicio.
- Checks obligatorios: CI, Profile Counts y Windows Setup (también tests visuales existentes).

## Pendientes ajenos a este bloque
Integrar fuentes completas de listas en tiempo real para nuevos objetivos, cerrar los dos robots mutadores con recuperación ante cierres inesperados y aceptación física en Windows, y release final sólo con autorización. Issues #164/#176 siguen abiertos.
