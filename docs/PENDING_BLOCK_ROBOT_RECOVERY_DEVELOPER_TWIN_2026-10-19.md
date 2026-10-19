# InstaCleaner — Bloque de recuperación y auditoría (2026-10-19)

Estado: **ESPECIFICADO / NO IMPLEMENTADO / NO VALIDADO**. Referencias: issue #133, PROJECT_LOG.md, docs/CURRENT_HANDOFF.md. Versión estable referencial v120.53; v120.54 es reserva, NO autorización de release.

## Objetivo
Eliminar tandas que se atascan, reintentar fallos demostrablemente sin clic, conservar sesión Instagram y mejorar trazabilidad sin duplicar Unfollows ni falsear Reviewed.

## Invariantes obligatorias
- `opened`, `prefetched`, `attempted`, `review`, `robot_error` no constituyen Unfollow confirmado, ni Reviewed.
- Nunca repetir un clic de Unfollow/Cancel si hubo clic o hay incertidumbre. Ante dudas: comprobación read-only, mantener journal y señalar incertidumbre.
- No entrar a la sesión de otra cuenta, no evadir challenges/CAPTCHA, no registrar cookies/tokens en logs/exportaciones.
- `already_not_following` requiere identidad exacta, propietario autenticado y botón de relación correcto observado de forma estable; no hace clic; cuenta como sin acción, no como Unfollow.
- Aprobación final de Reviewed es decisión separada y explícita del propietario, solo si quedan comprobaciones suficientes.
- Historial, listas protegidas, decisiones, datos importados y registros anteriores sobreviven actualizaciones, recuperación y rechecks.
- El propietario prueba **releases oficiales publicados** (Setup/APK), nunca previews/Actions.

## BR-01 — Batch size persistente (P1)
1. Cambiar 20/30/40 debe persistir al cambiar módulo, iniciar/parar, refrescar polling y reiniciar la app.
2. Separar `preferred_next_batch_size` de `active_batch_size` inmutable para tanda en curso. No reemplazar una tanda creada de 40 con selección posterior de 20.
3. Los eventos de progreso nunca escribirán valores predeterminados (40) sobre preferencia editada; establecer precedence y contrato de serialización explícitos.
4. QA: seleccionar 20 -> poll -> navegación -> restart -> 20; tanda activa 40 -> preferencia 20 -> terminar -> siguiente tanda 20. Prueba de actualización desde journal existente.

## BR-02 — Recuperación de cola sin atasco (P1)
1. Cada perfil tiene estado persistido: queued, prefetched, opened, session_checked, relationship_checked, action_intent, click_possible, verified_terminal, safe_no_click_error, ambiguous, challenge.
2. `prefetched` se convierte en unidad recuperable con último timestamp, intento, ventana/tab y heartbeat. Expirar preparaciones huérfanas; no contabilizar como processed.
3. Ante `session_verification_failed` antes de cualquier clic, cerrar solo pestaña sin clic, registrar motivo, reintento acotado/backoff y continuar con otras cuentas elegibles si la identidad del owner es válida.
4. Ante sesión no autenticada, challenge, owner equivocado, perfil equivocado o clic ambiguo: pausa segura global; no forzar acciones.
5. Al restaurar después de crash, reconstruir estado desde journal de escritura anticipada y descartar solo handles comprobados sin clic.
6. QA: diez tabs, falla segura tab 2 -> avance a tab 3, no se quedan 8/10 prefetched; reinicio a mitad; conexión intermitente; challenge pausa sin clic.

## BR-03 — Una sola sesión de navegador (P1)
1. `Open profile` en Issue Review debe dirigir la misma instancia/contexto persistente del navegador automatizado; enfocar pestaña existente si hay una.
2. Si no hay sesión del robot, informar el estado real y abrir una instancia persistente controlada, no un navegador anónimo distinto sin explicación.
3. Contexto de IG por usuario seleccionado, sin mezclas de workspaces. Nunca mostrar ni exportar cookies, headers de auth, tokens o credenciales.
4. QA: iniciar sesión una sola vez -> Run -> Issue Review -> Open profile, misma identidad y sesión; relanzar Setup y comprobar persistencia; cambio de usuario no hereda sesión ajena.

## BR-04 — Reauditoría de tandas históricas (P1)
1. Clasificar cada entrada del journal: **sin clic demostrado**, **clic posible/ambiguo**, **confirmado**, **ya no seguido**, **sin evidencia suficiente**.
2. Fallos demostrablemente sin clic -> reintento automático elegible dentro de tanda autorizada; no pedir revisión individual.
3. Clic posible -> únicamente lectura de relación actual y validación sin clic; si no se puede resolver, escalar un único reporte.
4. `already_not_following` -> terminar sin clic y pasar al siguiente; no repetir acción.
5. Dedupe por `(owner_ig_id, workspace_id, username_normalized, batch_id, action_intent)`; conservar auditoría inmutable de eventos.
6. QA: lotes antiguos con 2 failed + 38 untouched; journal previo a esquema nuevo; no doble clic; ninguna transición convierte robot_error en Reviewed.

## BR-05 — Contadores y UI (P1/P2)
1. Paneles por ámbito: **tanda activa** versus **historial acumulado**. Definir matemáticamente queued, eligible, attempted, no-click rechecked, confirmed_unfollows, already_not_following, ambiguous, pending_owner_review.
2. Denominador único `batch_total`: processed = terminales verificados + terminales de error adjudicado (si se muestran aparte). `0/0` no es válido si hay tanda activa.
3. Reconciliar backend journal, polling y Desktop con snapshot versionado. Mostrar explícito `Actions` frente a `Read-only recheck`.
4. Añadir separación y wrapping a contadores en ventanas estrechas, sin rediseñar tema aprobado.
5. QA de snapshot: 40 total, 2 issues, 38 untouched -> 0 confirmed, 2 issues, 38 remaining; no aprobar 40/40; ningún contador salta al cambiar tab.

## BR-06 — Developer twin universal (P1 feature)
1. Instancia Developer separada de canal público, pero comparte el comportamiento y permite **iniciar sesión exactamente como usuario normal** mediante el flujo de producción permitido. Acceso developer protegido por autorización explícita y datos aislados.
2. Mapa de sección y subcomponente con selector visual para señalar problemas. Capturar `route`, `section_id`, `component_id`, versión, fecha, comentario del propietario y estado del reporte, con opción de adjuntar evidencia desensibilizada.
3. Auditoría automática: rutas, pantallas, estado de tandas, consistencia de counters, errores de consola/backend, persistencia, pruebas sintéticas del robot (no clics reales sin permiso), salud de importaciones y navegación.
4. Exportar un **prompt autocontenido para IA** con pasos de reproducción, sección exacta, severidad, errores y stack traces redactados, verificaciones observadas, pendientes y límites de seguridad. Incluir un manifiesto JSON para reimportar notas.
5. Toda observación manual sobre sección específica persiste entre reinicios, upgrades y sesiones; no se pierde en exportación. Redacción automática de cookies, sesiones, archivos privados y usernames salvo consentimiento.
6. QA: iniciar sesión como usuario, cambiar pantalla, comentar un control, reiniciar, recuperar anotación, ejecutar auditoría, exportar y reimportar sin pérdida; impedir ingreso developer sin autorización; garantizar ausencia de secretos.
7. Contrato de producto transversal: replicar la especificación de Developer twin en Michel's Lab master por separado; no afirmar que ya existe en todas las apps.

## BR-07 — Release y pruebas (P1)
- Tests unitarios de máquina de estados y persistencia; integración Python/Chromium offline EN+ES y fixtures ambiguas; Windows Setup **instalar -> arrancar instalado -> pruebas funcionales -> upgrade/uninstall**; pruebas Desktop y Android donde corresponda; regresiones de identidad/seguridad y UI compacta.
- No afirmar que los tests sintéticos verifican Unfollows reales. La prueba final del usuario se realiza sobre release oficial publicado.
- Antes de publicar: PR/commit, same-SHA CI, checksums, identificación de signing Android y validación exacta de assets; **solo con nueva autorización explícita del propietario**.

## Secuencia de ejecución propuesta
1. Corregir separación de `active_batch_size` y preferencia + pruebas.
2. Corregir ciclo de vida `prefetched` y recuperación pre-click + pruebas.
3. Unificar Chrome manual/automático y verificación de owner.
4. Implementar reconciliación segura de tandas viejas + contadores de progreso.
5. Desarrollar Developer twin: anotaciones persistentes y exportación auditada.
6. Validar todos los flujos en instalador real desde CI y entregar release **solo cuando esté autorizado**.

**Esta especificación no equivale a código corregido ni a pruebas ejecutadas.**
