# Granada — lista de fin de tanda: verificar primero

Fecha: 2026-10-30. El usuario pide no recorrer decenas de filas verdes buscando las amarillas.

## Orden visual predeterminado

1. **⚠ REVISAR (amarillo):** `review`, `error`, `blocked`, cualquier observación read-only no confirmada y toda acción con clic incierto que el backend mantiene como Review.
2. **○ Sin comprobar:** `pending`, todavía sin resultado.
3. **◌ No disponible:** `profile_unavailable` únicamente cuando no existe una intención de clic anterior incierta. La observación unavailable tras posible clic permanece Review por contrato anterior.
4. **✓ Confirmado (verde):** `ok`, `already_not_following`, `already_not_requested` con evidencia concluyente, nunca una observación read-only no verificada.

El orden *dentro de cada categoría* conserva el orden original de selección. Las listas se reconstruyen en pantalla a partir de los resultados guardados, sin cambiar `batch.targets` ni `action_results` ni archivos del journal. Los botones de confirmación, reintento explícito, protección y reanudación no reciben cambios. La lista principal `igcAutoReviewDialog` y el panel por cuenta `igcDawReviewList` comparten la misma prioridad de estados.

## Pruebas

- `tests/automations-execution.test.cjs`: resultado verde al comienzo del lote se desplaza al final; Warning y otras observaciones no concluyentes arriba; caso 'unavailable tras posible clic' permanece amarillo arriba; lote mixto con dos Reviews, dos pending, unavailable y tres verdes conserva orden estable y JSON inmutable.
- `tests/dual-action-windows-panel-browser.test.cjs`: Chrome real sin Instagram; el servidor falso entrega una cohorte con verde al principio, y la lista local debe mostrar Review → Pending → verde, mientras la autorización `start-one` mantiene los objetivos originales y la cuenta intactos.

No implica ejecutar acciones en Instagram. Sin release hasta validar CI y Windows.
