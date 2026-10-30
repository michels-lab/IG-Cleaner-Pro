# Granada — Dos reservas de acción bajo el mutex global heredado

**Fecha:** 2026-10-30. **Estado:** contrato de infraestructura exclusivamente, sin habilitar clicks.

## Principio de compatibilidad

Instalaciones Windows anteriores (versión pública y Developer) reservan
`.instagram-action-admission.lock`. **No se puede eliminar ni sustituir**
esa barrera: hacerlo permitiría un binario anterior operando a la vez que dos
nuevos, sin compartir la misma evidencia de exclusión de mutaciones.

La nueva clase `SharedGlobalActionCohort` mantiene la barrera **global**
durante la vida de ambos scopes de un único proceso Windows, y reserva además
cada archivo `.instagram-action-<SHA256(owner\0account)>.lock` ya existente.
Si A termina antes que B, B sigue protegido tanto del binario antiguo como de
una tercera tarea. Si el proceso cae, Windows/Linux liberan todas las reservas
de kernel al cerrar los handles.

## Garantías automatizadas

- Sólo dos owners/workspaces distintos admitidos por un coordinador; un mismo
  scope duplicado falla sin perder la primera reserva.
- Error de reserva del segundo scope nunca libera el global si el primero vive.
  Error de primera reserva sí deshace el global (ninguna reserva zombie).
- El mutex global sigue en BUSY incluso desde **otro proceso** mientras vive
  cualquiera de los dos; también bloquea `ScopedActionLease` legacy.
- Al terminar el último scope, global y scopes quedan disponibles otra vez.
- Muerte forzada del proceso libera el global y ambos scopes.
- Directorio canónico de journal obligatorio. Rechaza cambiar la raíz.
- Tests obligatorios en CI general, Profile Counts y Windows installer.

## Lo que explícitamente NO se habilitó

El módulo es infraestructura pura y `parallel_mutations_enabled:false`.
**Ningún robot, endpoint, UI o release lo utiliza todavía**. Faltan:

1. Probar `ActionRobot` contra un proveedor de lease inyectable y mismo
   contrato de evidencia click-intent / outcome, con hilos y crashes reales.
2. Probar dos Playwright persistentes separados, ambos con prueba de login
   independiente, sin compartir contador ni ventanas, y Stop/Pause por cuenta.
3. Diseñar un opt-in visible por propietario para mutación dual, no confundir
   supervisor read-only con mutación, nunca repetir click incierto ni eludir
   bloqueos/challenges de Instagram.
4. Aceptación física Windows del propietario y aprobación funcional completa;
   recién después de eso considerar una versión final conjunta Windows/Android.

No tocar la versión estable, no prerelease, no tocar Instagram real.
