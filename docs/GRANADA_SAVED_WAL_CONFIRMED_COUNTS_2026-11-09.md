# Operación Granada — conteo correcto de acciones confirmadas después de reiniciar Windows

## Error corregido
Después de guardar una acción real confirmada, el WAL conserva por diseño `click_intent` con `outcome_recorded=true`. La vista de dos cuentas en `DualActionWorkspaces._saved_cohort_summaries` clasificaba **cualquier** entrada con `possible_click=true` como advertencia antes de examinar su estado `ok`. Eso hacía que acciones realmente confirmadas aparecieran como amarillas y el conteo de éxitos pareciera inferior.

## Cambios
- Usar `ActionRobot.batch_review` como fuente de estados sanitizados; después, contar `status=ok` como confirmado **antes** de revisar la presencia de un WAL que ya terminó. La ruta original ya convierte un `ok` sin `outcome_recorded=true` en `review`, por lo que no se permite validar clics inciertos.
- Mantener precedencia de advertencia para `review`, `blocked`, errores y cualquier `possible_click` sin estado terminal válido, incluso si una inspección posterior ve una relación distinta.
- Prueba de Python sobre los dos workspaces reales y reinicio frío: un `ok` con WAL terminal confirmado se cuenta como verde; un `ok` forjado sin resultado se mantiene amarillo; un usuario sin acción permanece pendiente; `already_not_following` sigue como sin clic; la lectura no modifica un byte del WAL ni abre Chrome.

Sólo fuentes, tests y bitácora. No RC, release, APK ni instalación. Pendientes la aceptación del ZIP original y el flujo físico de Unfollow/Cancel Pending en las dos cuentas.
