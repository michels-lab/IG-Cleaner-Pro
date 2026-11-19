# Granada 2026-11-19 — No autorizar clic con cuenta contradictoria en otra pestaña Chrome

## Regresión original y causa
La ruta `_verified_action_owner` aceptaba inmediatamente un `signed_in_handle(page)` coincidente en la pestaña del **objetivo**, sin revisar las otras pestañas del MISMO contexto persistente de Chrome. Una cabecera lateral desactualizada puede seguir mostrando el propietario anterior tras cambiar Instagram en otra pestaña. La ruta de cache/sibling sí inspeccionaba contradicciones, pero estaba ubicada **después** del retorno temprano. Además, `_live_sibling_owner_proof` devolvía `unknown` si faltaba `ds_user_id` antes de evaluar un desafío o una identidad opuesta en hermanos.

## Corrección real (fuente)
- Antes de aceptar un dueño visible en la pestaña del objetivo, examinar pestañas Instagram hermanas: desafío de Instagram, password/login visible, e identidad de dueño distinta **bloquean** el resultado; cache invalidado.
- Separar prueba negativa de conflicto de la autorización positiva: aunque no haya cookie válido, sí se detecta un propietario distinto o desafío en una pestaña hermana. Sin cookie no se permite utilizar una pestaña hermana como prueba positiva.
- Si una prueba almacenada tenía un `ds_user_id` válido y el usuario ha cambiado el cookie del mismo contexto, una barra lateral todavía visible del dueño anterior tampoco autoriza la acción.
- No navegar a `/owner/` adicionalmente, no hacer clic, no leer cookies fuera del Chrome del robot ni guardar datos privados. El preflight de click sigue siendo conservador.

## Evidencia, límites y reentrada
`tests/test_action_owner_proof_reuse.py` añade cuatro regresiones con propietario visible + cambio de cuenta/challenge/login, sin cookie de sesión, hermano coincidente y sesión con cookie cambiada. Se ejecuta en el workflow de Windows integrado y en release (mismos archivos). Los resultados exact-head deben leerse del PR; no inventar éxito.

**No se han realizado clicks en Instagram real** ni se ha probado físicamente el cambio de cuenta. #230 y #377 permanecen abiertos para aceptación del dueño. El porcentaje de la ruta v120.81 **permanece 50% (6/12)**: mejora fuente/CI en un problema de seguridad transversal sin cerrar un hito de aceptación física. v120.80 sigue publicada, `release_hold=true`.
