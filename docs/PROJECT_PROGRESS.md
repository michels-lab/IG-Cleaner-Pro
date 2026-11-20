# InstaCleaner Pro — avance global verificable

**Granada 20-nov-2026 — desbloqueo del CI Windows (50% → 50%).** Se diagnosticó el bloqueo compartido de [PR #396](https://github.com/michels-lab/IG-Cleaner-Pro/pull/396) y [PR #397](https://github.com/michels-lab/IG-Cleaner-Pro/pull/397): `timeout-minutes: 35` cancelaba el job integrado de Windows antes de completar compilación/instalación, con tres subprocessos protegidos por límites propios de 600+240+900 s y dependencias previas. Se elevó **solo el presupuesto del job a 65 minutos**, preservando **todas** las pruebas individuales, y se sincronizó el archivo de workflow en ambas ramas para evitar conflictos de merge. CI nuevo exact-head: [#396 `7a28d4fd`](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44840304865) y [#397 `ad52281c`](https://github.com/michels-lab/IG-Cleaner-Pro/pull/397). Validación en ejecución; *no hay merge ni aprobación de Windows instalador afirmados todavía*. Los defectos corregidos en fuente son arranque/cierre de controlador Windows y compactación/rollback de Focus; la validación física real #371/#377/#360/#164/#172 y v120.81 siguen pendientes. Progreso 6/12 = 50% y versión pública v120.80 sin cambios.


**Granada P0 20-nov-2026 — 50% → 50% (6/12).** Fuente en [PR #396](https://github.com/michels-lab/IG-Cleaner-Pro/pull/396) (arranque/cierre Windows con dos slots, sin controlador local huérfano) y [PR #397](https://github.com/michels-lab/IG-Cleaner-Pro/pull/397) (HTML standalone + Desktop: historial v3 lossless, tandas compactas, evitar aperturas y contadores ficticios cuando quota rechaza el guardado). Ambas ramas tienen cambios y regresiones, con **QA exact-head en curso** al registrar este corte: CI Desktop de Focus y prueba visual HTML SUCCESS; queda QA Windows instalado y otras plataformas. No se fusionan o publican mientras falten gates. Auditorías en ramas: [Windows](https://github.com/michels-lab/IG-Cleaner-Pro/blob/granada/windows-startup-failure-recovery-20261120/docs/audits/2026-11-20-windows-startup-recovery.md) y [Focus](https://github.com/michels-lab/IG-Cleaner-Pro/blob/granada/focus-lossless-history-v3-20261120/docs/audits/2026-11-20-focus-lossless-history-v3.md). **No prueba física:** #371/#377/#360/#164/#172 abiertos. v120.80 última release estable; v120.81 retenida.


**Continuación QA 20-nov-2026 — 50% → 50% (6/12).** [PR #395](https://github.com/michels-lab/IG-Cleaner-Pro/pull/395) **FUSIONADO en `main`** como [`badf10cd`](https://github.com/michels-lab/IG-Cleaner-Pro/commit/badf10cd98b4bfc43c8879d162e83f994667de66) tras **5/5 controles exact-head SUCCESS** (CI Desktop/Android + Supabase RLS, visual Desktop y Android). La prueba real de ambos entrypoints preserva 789 revisiones anteriores y suma 30 nuevas frente a quota, recarga y A→B→A. [Auditoría local](audits/2026-11-20-focus-789-existing-decisions.md). **No es prueba Chrome real** ni arregla la cuota física; #360/#371/#377 y Unfollow/Cancel siguen abiertos. Versión pública v120.80; v120.81 retenida.


**Granada 2026-11-19 — guard de identidad Chrome del robot:** [PR #394](https://github.com/michels-lab/IG-Cleaner-Pro/pull/394) **fusionado en `main`** como `3c6ad280f64fe7b870dee61b587575655ce47beb` tras **5/5 workflows exact-head SUCCESS**, incluyendo Windows Setup integrado y Chromium offline. Corrige el retorno prematuro de un dueño visible, ahora bloqueando clics si otra pestaña Instagram evidencia una cuenta distinta/login/challenge incluso sin cookie, o si el ID de sesión ligado cambió. No hace clics reales ni certifica dos cuentas físicas. **Progreso global: 50% → 50% (6/12 hitos)**; #230/#377 y otros P0 físicos siguen ABIERTOS. La estable pública sigue siendo v120.80; `release_hold=true` y v120.81 no se publicó.

**Corte:** 2026-11-19 · **Ruta:** cierre P0 y siguiente versión final estable v120.81.

## 50% estimado — 6/12 hitos de aceptación verificados

Fase actual: **fuente integrada en main y CI aprobada; validación física de propietario, funcionamiento real de robots y publicación de v120.81 pendientes**.

**Cómo se calculó:** los 12 hitos explícitos abajo tienen el mismo peso; solo se suma un hito cuando su tipo de evidencia se cumplió. Los primeros seis son **fuente/CI**, no aceptación humana ni acciones reales. No usar esto como % universal del código ni inferir que la app puede operar Instagram sin supervisión.

| N.º | Hito / criterio de aceptación | Resultado |
| --- | --- | --- |
| 1 | [Import ZIP y aislamiento lógico de perfiles en fuente/CI](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80) | ✅ Fuente/CI verificada |
| 2 | [Elección de ventana primaria/secundaria y UI independiente, CI offline](https://github.com/michels-lab/IG-Cleaner-Pro/issues/377) | ✅ Fuente/CI verificada |
| 3 | [Perfiles reales de navegador del robot separados por ventana](https://github.com/michels-lab/IG-Cleaner-Pro/pull/391) | ✅ Fuente/CI verificada |
| 4 | [Registro de intención previa al clic y exclusión entre procesos](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) | ✅ Fuente/CI verificada |
| 5 | [Cancel Batch guardado recuperable tras reinicio con bloqueo de WAL](https://github.com/michels-lab/IG-Cleaner-Pro/pull/392) | ✅ Fuente/CI verificada |
| 6 | [Confirmación masiva Reviewed/Pending atómica y Double Check sin borrar decisiones anteriores](https://github.com/michels-lab/IG-Cleaner-Pro/pull/393) | ✅ Fuente/CI verificada |
| 7 | [Focus 30 bajo cuota real con historial grande, exportación y recuperación sin pérdida](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371) | ⏳ Pendiente |
| 8 | [Dos ventanas Windows simultáneas con sesión IG A/B real y UX Automations aceptada](https://github.com/michels-lab/IG-Cleaner-Pro/issues/377) | ⏳ Pendiente |
| 9 | [30 revisiones reales, Recheck/Double, refresh/reinicio A→B→A sin rebote](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360) | ⏳ Pendiente |
| 10 | [Unfollow real confirmado por objetivo y journal sin falsos OK/repeticiones](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) | ⏳ Pendiente |
| 11 | [Cancel Pending real, estado ya no solicitado y no reabrir perfiles resueltos](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) | ⏳ Pendiente |
| 12 | [v120.81 oficial: QA de distribución/aprobación de gates, activos y verificación posterior](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80) | ⏳ Pendiente |

## Evidencia y punto de reentrada

- Fuente: #391 (sesiones independientes), #392 (Cancel Batch con WAL), **#393 integrado** en `fd52d8760ae0bc7e6863db123e17cd722b4afd8a` (Focus atómico).
- #393: **6/6** workflows en SUCCESS en el SHA de PR, incluyendo Windows integrado. Una prueba offline/CI jamás equivale a dos cuentas de Instagram reales.
- Última publicación confirmada: **[v120.80](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80)**. v120.81 **no publicada**; `release_hold=true`, `owner_final_acceptance=false`.
- En la próxima Granada: verificar primero la CI/head/PRs en vivo; luego resolver #371 (cuota en navegador real), #360 (30 revisiones sin rebote), #377 (dos ventanas reales), #164/#172 (Unfollow/Cancel Pending con evidencia). No borrar historiales ni dar por hecho trabajo físico no realizado.
- Registro machine-readable en [`.michelslab/project-progress.json`](../.michelslab/project-progress.json). Tablero global: [Michel-Software-Standards](https://github.com/michels-lab/Michel-Software-Standards/blob/main/reports/PROJECT_PROGRESS.md). La bitácora local sigue siendo la fuente de detalle.
