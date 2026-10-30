# Operación Granada — retener identidad y WAL al rechazar tandas

**Fecha:** 2026-10-27. **Ámbito:** motor de acciones Windows `ActionRobot`, compatibilidad con Developer y dos perfiles de Chrome. **Estado:** fuente en rama, pendiente CI exacta. **Prohibición:** no publicar release.

## Defecto localizado

`ActionRobot.start` vinculaba `self.owner/account/handle/task` al workspace entrante **antes** de comprobar si todos sus objetivos ya tenían un resultado persistente. Cuando el robot rechazaba la tanda sin usuarios vírgenes, podía quedar mostrando una identidad nueva a pesar de no haber arrancado ninguna operación; el estado previo de la sesión quedaba confundido. El problema también afecta a cualquier excepción posterior durante lectura/guardado de protección.

## Corrección aplicada

1. Se mantienen las validaciones de journal, visitados, protecciones y cohorte por `owner+account+task`. La comparación de no-replay y rechazo por protegidos ocurre **antes de alterar el estado activo del robot**.
2. El ID de cohorte siguiente se calcula en variable local. Se guardan los registros aprobados y la protección explícita en el scope solicitado; la identidad en memoria solo se cambia después de completar satisfactoriamente la lectura/escritura de seguridad. Rechazar una tanda no destruye ni rebautiza la anterior.
3. `ScopedActionLease` introduce bloqueo **global heredado + bloqueo adicional por owner/workspace** con nombre derivado de SHA-256. El orden es global → scoped, inverso al liberar. En Windows se usan locks del kernel (y en POSIX `flock`); fallar el segundo lock libera el primero. Si muere el proceso, ambos dejan de bloquear. Nombres de cuenta no aparecen en los filenames.
4. Se **conserva expresamente el global** que ya usan las versiones instaladas y Developer: dos cuentas tienen exclusividad de registros identificable, pero **NO ejecutan dos unfollows simultáneos**. El bloqueo global es imprescindible hasta completar la migración, el journal multiworker y la verificación de Chrome por cuenta. No permitir a una versión nueva interpretar el bloqueo por cuenta como permiso de mutación.
5. Pruebas offline reales de procesos/hilos: compatibilidad global, identidad separada, crash, adquisición parcial fallida, rechazo de tanda ya revisada, protección bloqueante y control del lock durante toda la tarea. Cero solicitudes a Instagram y cero clicks.

## Exclusiones y punto de reentrada

- El siguiente bloque verdaderamente concurrente requiere journaling y confirmación por **owner+workspace**, verificación de sesión/target **por clic**, límites y cooldowns de la misma sesión/servicio, pruebas de arranque y recuperación de cada worker, y aceptación del propietario con su Windows/Chrome.
- No se toca importación ZIP, listas Followers/Following, protected guard, user Chrome, ejecutables, updater, Android o versión del producto.
- Validar exact HEAD con CI general, Profile Counts, Windows Setup instalado y Developer, contratos de autenticación, historial y no replay. Solo después de CI verde fusionar a main.
- Seguir dejando #164 y #176 abiertos; queda pendiente la aceptación física de Unfollow y Cancel Pending. Nada de releases hasta que el propietario confirme la app completa.
