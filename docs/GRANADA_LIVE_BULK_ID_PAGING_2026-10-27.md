# Operación Granada — lectura masiva de seguidores/seguidos sin perfiles individuales (2026-10-27)

## Problema observado por el propietario

En la versión estable [v120.69](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.69), **Automations → Verify live Followers and Following** mostró: `Live list reached its 250-pages safety limit. No negative conclusions`; no se obtuvo ninguna instantánea completa. El límite contaba *páginas HTTP*, no usuarios: pedir `count=100` no implica que Instagram entregue 100 usuarios por respuesta. Por tanto, **250 páginas no equivalen necesariamente a 25.000 perfiles**. Esto no demuestra que la app estuviera abriendo perfiles individuales; su implementación anterior ya hacía JSON GET de listas, pero tenía un límite demasiado rígido.

## Diseño propio a partir del principio del código que el usuario compartió

- **NO** copiar el bundle Webpack o su código literalmente. Conservar solo el principio: desde el Chrome local autenticado por el usuario, consultar la colección `followers` y `following` mediante lectura **same-origin de páginas JSON de muchos usuarios por solicitud**, con cursor `max_id`; nunca `page.goto` a cada perfil para obtener la lista.
- La consulta intenta solicitar hasta 200 miembros por página y acepta que Instagram entregue menos; aumenta el presupuesto seguro a 1500 páginas y 100.000 miembros únicos por lista. No intentar saltar límites ni desafíos: mantener 800 ms entre páginas, GET únicamente, 20 s de timeout por solicitud, detenerse ante 429/error/desafío/sesión diferente/cursor inválido/repetido/ocho páginas sin nuevos miembros.
- Reconocer al miembro por el ID numérico estable `pk/id/pk_id` además de validar el username. **Comparar por ID**, evitando falsos no-seguidores cuando una cuenta cambia de usuario mientras se descargan las dos listas. Guardar en la UI solamente usernames, conjuntos completos, totales y fecha; jamás tokens, cookies o datos crudos de la sesión.
- El Worker informa progreso con `followers/following`, cantidad de cuentas únicas cargadas y páginas JSON consultadas; no infiere que la cantidad de páginas corresponda a perfiles individuales.
- **Solo** cuando ambas listas confirman paginación terminal, el mismo owner sigue autenticado y hay evidencia de ID consistente, escribir la instantánea atómica `igc-live-relationships-v1` existente. Una lectura incompleta no sobrescribe un respaldo completo anterior ni genera categorías «no me sigue».
- No modificar robots de Unfollow/Cancel, ZIP, historial, WAL, cuentas protegidas, autenticación ni Android. Esta mejora pertenece a una **futura versión** y no altera la v120.69 publicada.

## Protección frente a restricciones de Instagram (v120.70)

En el código que compartió el propietario se observó el principio de escalonar ciclos de búsqueda, descansar tras varios ciclos y reducir solicitudes cuando Instagram devuelve un bloqueo o `rate limit`. Esta implementación independiente añade pausas **conservadoras, no equivalentes a una cuota publicada por Instagram**: 2.5 s entre respuestas paginadas, 12 s cada cinco páginas y 90 s cada 25; respetar `Retry-After` con mínimo 30 minutos tras `429`, `403`, `503` o `feedback_required`, sin reintentar automáticamente una respuesta limitada. Se guarda el tiempo de enfriamiento **por usuario/cuenta y globalmente por sesión compartida de Chrome**: cambiar de workspace o reiniciar la app no evita la espera. También se interpreta `Retry-After` tanto en segundos como en formato fecha HTTP y se reconoce `feedback_required` o los mensajes `please wait` del cuerpo. Tras lectura correcta, mínimo 15 minutos antes de iniciar otra. Stop puede interrumpir el descanso al instante, sin guardar listas parciales ni fingir que cambiaron relaciones.

El escaneo es voluntario, solo lectura, y no usa proxies, rotación de IP ni técnicas para esquivar desafíos. No se puede garantizar que Instagram no limite o suspenda una cuenta: las rutas usadas son privadas y no documentadas.

## Pruebas offline y límites

- 275 páginas JSON con un usuario cada una completan (supera el antiguo tope de 250), sin `page.goto` de ningún perfil.
- Una prueba de renombrado entre Followers y Following mantiene identidad numérica y calcula correctamente no-followback/Fans.
- Un cursor con páginas repetidas sin nueva membresía falla rápido; ID ausente/duplicado y respuesta parcial fallan cerrados. Mantenemos controles históricos de sesión exacta, autorización, aislamiento entre dos cuentas, cohabitación Windows/Android y preservación del journal.
- **No validado con Instagram real todavía:** API privada no documentada puede cambiar, fallar, dar 429 o devolver menos miembros de los esperados. La prueba física del usuario (misma cuenta Chrome de la app) sigue pendiente. No prometer actualización del instalador antes de pasar CI exacto y generar una siguiente release FINAL normal independiente; prohibido RC.
