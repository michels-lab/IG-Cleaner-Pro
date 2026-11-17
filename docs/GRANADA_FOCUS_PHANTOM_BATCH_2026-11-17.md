# GRANADA — Focus 30 no abre / número baja y se regenera (2026-11-17)

## Reproducción informada por el propietario

- Plataforma afectada: **HTML standalone v120.77** abierto en un navegador; otra cuenta de Instagram, en **otro navegador**, funciona.
- Pasos: Focus 30 → cuadro nativo `BATCH PREVIEW · foco 30` con 30 relaciones verificables y nunca revisadas → Aceptar.
- Resultado observado: **ninguna pestaña Instagram**, **no aparece el cuadro Reviewed**; los abribles **disminuyen**. **Recargar restaura el número anterior**. Sin evidencia de que esos perfiles se hayan revisado.
- Pantalla previa: ~69 abribles, 789 revisados. Contadores proporcionados por el propietario, no una prueba ejecutada contra su sesión.

## Causa identificada en código de v120.77

`setActiveFocusBatch()` creaba `activeFocusBatch` en memoria, llamaba `recordRowsHistory('open')` —escritura de `profileHistory` en localStorage—, y **solo después** llamaba a `saveActiveFocusBatch()`. Si la escritura del historial lanzaba excepción, `openConfirmedFocusRows()` terminaba antes de `window.open` y antes de `showSafeFocusPopup`; sin embargo, `activeFocusBatch` ya restaba 30 del pool visible. La recarga descartaba esa cohorte no persistida. Esto reproduce **la secuencia de estados** descrita; que en el navegador del propietario fuera específicamente `QuotaExceededError` sigue pendiente de su consola, y no se afirma como hecho confirmado.

De forma separada, `window.open` tampoco tenía contención de excepciones y podía impedir que apareciera Reviewed. La aplicación no puede distinguir una pestaña abierta con `noopener` de una bloqueada usando solo el valor devuelto por `window.open`; no se declara éxito de apertura ni revisión automática.

## Implementación fusionada

- **PR [#366](https://github.com/michels-lab/IG-Cleaner-Pro/pull/366) — merge en main `bc75385c0d1a78e2e64124b698b2aa69b6057341`**.
- Persistir primero la cohorte `opened_unconfirmed`, **antes** de añadir historial de tentativas. Si no puede guardarse, revertir el estado temporal, no abrir perfiles ni modificar decisiones Reviewed y presentar mensaje recuperable.
- Mostrar Reviewed con enlaces directos por perfil **antes** de las peticiones de Chrome. Aislar una excepción por pestaña sin esconder el diálogo.
- `Could not review yet` libera **solo** el intento no confirmado de ese módulo; nunca vuelve a meter perfiles efectivamente revisados en Focus ordinario. Si falla guardar esta liberación, revertir en memoria y conservar la tanda activa.
- En todos los puntos de apertura (Focus normal, Recheck, Double Check, Pending segunda ronda y variantes históricas), comprobar la persistencia **antes de abrir y de avanzar ciclos**.
- Tests negativos añadidos: `tests/focus-confirmation-storage-popup-regression.test.cjs`, `tests/focus-failed-attempt-requeue.test.cjs`, `tests/focus-storage-all-modes.test.cjs`, conectados al flujo CI de escritorio.

## Evidencia y límites

**Exact head de implementación:** `91a5a8bc31577ba6de6375baf9211be50dd54dbb`. **9/9 checks GitHub del PR SUCCESS** antes de merge: contrato escritorio con tests nuevos, contrato offline, navegador renderizado, instalador Windows integrado, RLS, build Android/emulador/QA. GitHub PR merge SHA anterior. La compilación en Actions no es prueba del navegador local del propietario.

**Última versión FINAL publicada:** [v120.77](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.77), tag `7326d3293fabc606ddf336cfedc35c324b63795e`, 9 assets públicos, publisher `43811216485` exitoso. Ese HTML **no contiene** el arreglo fusionado. Próxima versión reservada: **v120.78, no publicada**, autorización anterior consumida. Sin RC/Developer.

**Issue [#360](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360) sigue ABIERTO** para rebotes posconfirmación, sincronización, importaciones y QA real de dos cuentas; este arreglo resuelve un subcaso de cohortes temporales y excepciones de almacenamiento. QA real de ventanas Chrome, recuperación de 789 revisiones y preservación A→B→A requiere validación del propietario **sobre siguiente release estable oficial**, no en un artefacto candidato. No borrar datos del sitio ni reiniciar progreso; exportar respaldo antes de cualquier migración.

## Prevención / reentrada

`activeFocusBatch`, `profileHistory` y `reviewedMeta` tienen semánticas diferentes: *intento de apertura ≠ perfil abierto ≠ decisión revisada*. Nunca rebajar `available` por un estado temporal que no puede persistir. Fallos de escritura deben ser explícitos y no mutar el historial validado. Mantener tests de fallos y CI exact-head obligatorios para cambios posteriores.
