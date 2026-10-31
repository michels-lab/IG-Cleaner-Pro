# Granada — Cancel Pending se detiene ante diálogo Unfollow inesperado

**Incidente reportado (30 de octubre de 2026):** con `Cancel Pending Requests` activo y 60 perfiles en cola, después de aproximadamente 30 cancelaciones observadas, el panel mostraba `REVIEW`, `Already attempted: 35`, `Ready: 25`, y Chrome presentaba **«¿Dejar de seguir a __cesarin_?»** (botón rojo «Dejar de seguir»). Esta captura NO prueba que los 35 intentos hayan sido exitosos. Tampoco permite conocer la causa remota del cambio de estado en Instagram.

## Por qué ocurrió el bloqueo
`perform_visible_action(..., task="cancel")` selecciona el control *Solicitado / Requested*. Instagram puede cambiar la relación a *Siguiendo / Following* cuando acepta una solicitud, incluso mientras el sitio se hidrata. Un clic posterior puede abrir un cuadro de **Unfollow real**. El código existente `_request_cancel_confirmation` no acepta como cancelación de solicitud el rótulo Unfollow aislado: exige contexto visible de «volver a solicitar seguimiento» y @usuario exacto. Por lo tanto la seguridad preexistente **NO hizo el segundo clic** y puso el resultado en REVIEW. Los objetivos sin verificar mantienen una pestaña Chrome abierta y el worker espera que se cierre manualmente; por eso parece congelado. El journal debe conservar el `click_intent` armado antes del primer clic.

## Corrección
- Nueva comprobación de `Requested` después de una breve estabilización y justo antes de armar el primer clic de Cancel; rechaza Following, cuenta errónea, desafío, redirección, objetivo incorrecto o control Requested desaparecido.
- Si **después** del primer clic aparece el cuadro Unfollow sin contexto de cancelación inequívoco, el segundo clic permanece prohibido. El incidente queda en REVIEW con código específico `pending_wrong_relationship_dialog`, detalle que indica explícitamente «NO pulse Dejar de seguir», y el `click_intent` original bloquea replay.
- El estado de revisión final conserva una explicación visible de «unexpected Unfollow confirmation» en vez de únicamente «tabs remain open».
- Se mantiene el flujo legítimo *Requested → confirmación específica → lectura/verificación*.
- **No se habilita el reintento automático de una intención de clic incierta** ni se presume éxito; los perfiles que no se llegaron a procesar siguen pendientes de una tanda posterior con consentimiento independiente.

## Pruebas
Nueva prueba Playwright sobre Chrome real **totalmente offline**: (1) diálogo Unfollow aislado en español/inglés debe dar REVIEW y jamás tocar botón rojo (fases WAL sólo `relationship_control`); (2) Requested cambia a Following antes de la primera acción: cero clics y código `pending_already_following`; (3) cancelación explícita real del fixture mantiene los dos clics aprobados y resultado verificado. La CI de Windows debe ejecutar la regresión junto a la suite anterior.

## Qué debe hacer el usuario en la ejecución actual
No pulsar «Dejar de seguir». El botón gris «Cancelar» de Instagram sólo cierra ese diálogo; no equivale a Cancel Pending de InstaCleaner. Revisar manualmente el perfil y la lista guardada, no tratar los 35 intentos como confirmados, no usar Resume para repetir el objetivo incierto. `Pause` cierra Chrome pero conserva el WAL. Ninguna modificación en GitHub actualiza automáticamente la instancia Windows ya abierta.
