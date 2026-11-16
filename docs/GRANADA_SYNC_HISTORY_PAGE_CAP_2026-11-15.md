# Operación Granada — integridad de revisiones y paginación (2026-11-15)

## Estado

**Código integrado en `main`; NO es un nuevo release.** Último release publicado y comprobado al abrir este bloque: `v120.75`. No se ha verificado funcionamiento con las sesiones reales del propietario en su Windows/Android.

## Causa raíz y solución

- La API PostgREST puede responder menos filas que el `limit=1000` solicitado por un límite servidor. Avanzar el `offset` en 1,000, o terminar solo porque la página tiene menos de 1,000, podría omitir registros.
- `pullEvents()` y `readCompleteProfileState()` ahora avanzan el cursor por el **número real de filas recibidas** y solo consideran terminada la lectura cuando llega una **página vacía**.
- La descarga de revisiones compara el total de registros de la cuenta seleccionada con el resumen autenticado de la misma base; un resultado parcial o incoherente falla cerrado. Una página inválida o identificadores duplicados abortan la fusión antes de modificar los registros locales.
- `pushProfileState()` consulta el historial remoto completo antes de subir datos, sin sobreescribir una revisión más nueva.
- La UI diferencia `historial histórico de revisiones de todas las secciones` de `revisados vigentes de Following`; estos contadores no deben coincidir necesariamente. Se aclaró que el total de `espacios de Instagram` no representa el número de seguidores o seguidos.
- El sincronizador muestra cuántos registros históricos recuperó y cuántos de la lista Following actual cumplen los criterios conservadores de revisión.

## Evidencia automatizada

- Tests reales de los selectores del código distribuible: `tests/cloud-review-pagination-9896.test.cjs`, `tests/cloud-audit-pagination.test.cjs`, `tests/cloud-review-monotonic.test.cjs` y `tests/review-current-vs-historical.test.cjs`.
- Escenarios de páginas de 1,000 y 500 filas, repeticiones de página, interrupción, comparación antes de subir, y separación de métricas de historial/Following.
- Workflow `IG Cleaner Pro CI` **SUCCESS** para el commit `048e9b8e9f76623521c297acfe1e1fae12247a28`: https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/43788671286 (Desktop contract, aislamiento Supabase, Android build). UI de escritorio también obtuvo SUCCESS en el commit de tests `fd96b1f`: https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/43788657463.
- **Sin pruebas de cuentas reales en Instagram** y sin mutaciones de producción durante este bloque. Las consultas realizadas para diagnóstico fueron de solo lectura.

## Pendientes reales

1. Instalar una futura versión publicada con estas correcciones; abrir la cuenta correcta y observar sincronización completa, persistencia después de cerrar/reiniciar, y contadores consistentes en cambio A→B→A.
2. No asumir que todo el historial remoto corresponde a cuentas aún incluidas en el export actual: comprobar vigencia de relación, fecha y modo antes de contar como revisado.
3. Verificar robots Unfollow/Cancel Pending y ausencia de tandas recicladas en la instalación del propietario; las pruebas Chromium simuladas no prueban aceptación real de Instagram.
4. Las ediciones Developer fueron canceladas por instrucción del propietario; no reabrirlas como requisito del futuro release.

**Política de publicación:** no declarar una nueva versión hasta que aparezcan su tag público, binarios firmados e integridad. `v120.75` no contiene las correcciones documentadas aquí.
