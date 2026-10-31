# Granada — revisión automática de una tanda terminada por cuenta

**2026-10-30. Estado: PR dependiente de modo paralelo, sin publicación.**

En la app nativa Windows, el panel de dos acciones ahora consulta periódicamente, **sólo si ya observó algún robot en marcha**, el estado de las dos cuentas por el puente protegido con token local. La consulta es exclusivamente `GET /api/actions/dual-action-workspaces/status`; no abre Chrome ni visita Instagram.

### Comportamiento
- Al completar una tanda, llegar a un estado de revisión, error, bloqueo o detenerse después de estar en marcha, aparece una ventana oscura **por cuenta** con el @handle, tarea y contadores de revisados, pendientes e incidencias.
- Consulta de forma independiente el **journal guardado original** mediante `review-one` y presenta hasta 50 @usuarios con **OK verde**, **REVIEW amarillo** o **NO DISPONIBLE gris**, más fecha/hora. Permite abrir la lista íntegra a través del botón de revisión existente.
- No se ejecuta `approve-one`, `start-one`, un unfollow, ni ninguna modificación automática de resultados al abrir, cerrar o recorrer el popup. Aprobación final y reintentos siguen requiriendo confirmación explícita en el panel original.
- Un robot puede terminar mientras el otro sigue; los avisos quedan en cola en lugar de sustituirse. Revisión seguida de Pausa no genera un aviso duplicado de la misma tanda.
- Los errores del puente no cambian el journal ni activan acciones; el usuario puede revisar manualmente. El polling no se ejecuta cuando la app está oculta o durante otra acción explícita de la UI, y no hace peticiones cuando no se observan workers activos.
- No se confunde `running:false` con `status:ok`: una finalización incierta puede seguir amarilla hasta que el usuario la inspeccione. `review-one` sólo muestra el resultado ya persistido.

### Criterios de aceptación
Prueba Chromium del HTML real de Windows con un puente falso offline: ambas cuentas arrancan por separado, A completa mientras B sigue activo, el modal lee WAL sin aprobar ni reejecutar, A no dispara avisos duplicados, B entra en Review y luego Paused sin repetir el popup; el botón Revisar lista completa llama al control de lectura original. Pruebas estáticas de la inyección nativa y gate obligatorio del instalador Windows.

**Base de integración:** este PR se reconstruyó como un único cambio sobre `main` tras fusionar el modo concurrente #293. No incluye modificaciones a los archivos del auditor File Steward ni altera el control de versiones. La verificación del nuevo commit debe repetir Windows y los checks obligatorios antes del merge.

**No hay release**, pruebas sobre perfiles reales ni aceptación física todavía. Issues #164/#176 continúan abiertos.
