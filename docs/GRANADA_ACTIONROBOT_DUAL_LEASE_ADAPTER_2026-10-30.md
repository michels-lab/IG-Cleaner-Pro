# Operación Granada — ActionRobot lease adapter + two-worker offline acceptance

**Fecha:** 2026-10-30. **Estado:** rama de desarrollo, sin release.

## Cambio real
`ActionRobot.__init__(..., *, lease_factory=None)` acepta un proveedor opcional interno de reserva de acciones. **Por omisión sigue siendo `ScopedActionLease`**, es decir, adquiere el mismo mutex global heredado y su lease por propietario/cuenta. No hay cambios en el puente Windows, UI, scripts Android ni contrato de inicio clásico.

El coordinador `SharedGlobalActionCohort` integrado en PR #289 suministra `cohort.lease` únicamente a instancias creadas en pruebas aisladas. Sus dos instancias reales de `ActionRobot` siguen ejecutando el método `start`, el preflight de owner/account, WAL, lista de protegidos, pausas y el thread `_run_with_lease`. El cuerpo `_run` que abriría Playwright **se reemplaza por eventos de prueba sin red**. No se abre Instagram ni se modifican relaciones.

## Contratos ejercitados
- Dos `ActionRobot.start` con diferentes cuentas del mismo propietario pueden coexistir sólo si la fábrica es inyectada internamente; mientras A o B viva, los binarios heredados públicos/Developer (lease global antiguo) no pueden iniciar.
- Terminar A no libera el global mientras B continúe; terminar B sí lo libera sin locks zombies.
- Rechazar un segundo propietario, un objetivo protegido, una sesión Chrome ocupada, o un tercer proceso no altera el journal ni libera el trabajo activo.
- Los dos directorios Chrome, archivos de journal y estados mutables son independientes.
- Un `ActionRobot` construido sin argumento adicional conserva el bloqueo global anterior; si se inyecta un proveedor inválido, falla cerrado.
- Matriz CI general, Profile Counts y Windows Setup debe pasar usando el SHA exacto.

## Qué **NO** cambia todavía
El `DualActionWorkspaces` creado por la app **no recibe** `lease_factory`, por tanto sigue serializando y rechazando el segundo Unfollow/Cancel. La edición Developer tampoco recibe el proveedor experimental. La implementación no añade endpoint, botón, permiso ni bandera que active mutaciones simultáneas.

Próximo bloque: integrar ambos supervisores tras pruebas completas de WAL/cancelación y de identidad separada, con consentimiento expreso por tanda; verificar navegador real en Windows por el propietario. No declarar terminado, no publicar release, issues #164/#176 abiertos.
