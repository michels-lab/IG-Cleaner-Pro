# Operación Granada — auditoría de aplicación e integraciones ChatGPT

**Corte de evidencia:** 2026-10-21 UTC. **Tipo:** auditoría documental de árbol/README y últimos GitHub Actions consultados, NO prueba funcional en hardware, cuenta de cliente, ni validación completa del ejecutable. 

**Regla de costo:** usar primero las herramientas ya instaladas en ChatGPT Plus y los servicios existentes; **no contratar suscripciones extra**, activar facturación, subir de plan, comprar dominio ni desplegar sin autorización. Un plugin de ChatGPT no se incorpora automáticamente al código de la aplicación. “Instalado en ChatGPT” no prueba sesión activa, permisos o servicio operativo. [Bitácora central de ocho conectores instalados](https://github.com/michels-lab/Michel-Software-Standards/blob/main/docs/CHATGPT_PLUGIN_LEDGER.md). No guardar tokens ni datos de usuarios en documentación pública.

## Alcance y frontera
**IG Cleaner Pro** importa exportaciones y administra revisiones/tandas con Desktop/Android. No introducir CFD/OpenFOAM, audio/LouderMe ni misiones/Michel's Life. La automatización de relaciones sociales tiene riesgo real y requiere aceptación por el propietario, nunca probar clics destructivos sobre cuentas sin autorización expresa y controles.

## Conectores y servicios: decisiones por proyecto
| Herramienta | Condición comprobada | Aplicación real / cautela | Decisión |
| --- | --- | --- | --- |
| **GitHub (ChatGPT)** | Instalado/habilitado y usado | PR, CI, pruebas de robots offline, releases, bitácoras del Developer Twin | USAR |
| **Supabase (ChatGPT)** | Instalado/habilitado; código `supabase/` presente | Backend opcional de sincronización de estados derivados. Nunca afirmar que el ZIP original se sube; ver `docs/PRIVACY.md` y permisos reales | USAR SOLO si autorizado y necesario |
| **Spreadsheets / Documents** | Instalados/habilitados | Matrices sintéticas de fallos, diagnóstico exportable sin credenciales/datos de perfiles | OPCIONAL |
| **Gmail / Calendar / Contacts** | Instalados/habilitados | Sin necesidad para el robot ni para las listas de Instagram | NO INTEGRAR |
| **Vercel / otras apps sociales** | No instalados/conexión no verificada | No incorporar login por terceros ni nube nueva solo por recomendación | NO CONTRATAR |

**No existe aquí un plugin ChatGPT que sustituya el navegador de sesión de usuario, las pruebas de aceptación ni la autorización para realizar Unfollow.** El plugin Supabase no demuestra que el sync esté probado.

## Últimas comprobaciones consultadas
- HEAD consultado `de6343fe`: [File Steward #39669433636](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39669433636) **SUCCESS**.
- En el mismo corte, [IG Cleaner CI #39669433682](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39669433682), [Desktop rendered #39669433609](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39669433609) y [publicación gobernada #39669433591](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39669433591) figuraban **IN PROGRESS**. No extrapolar resultados posteriores de este documento: verificar en vivo al retomar.
- [File Steward #39664546396](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39664546396) anterior FAILURE al publicar informe por concurrencia; escaneo no halló cruce de dominio (0 hallazgos). Un éxito posterior no prueba botones del robot.
- README anunciaba **stable v120.54**; **v120.55 no debe proclamarse publicado** antes de verificar tag, activos y hashes. Aun publicado, el clic real sobre Instagram no queda validado por CI.

## Pendientes concretos
1. Inspeccionar todas las suites de HEAD y el release final antes de afirmar publicación (sin RC).
2. Respetar tamaño de tanda que seleccione el usuario, persistencia/reanudación de 10 perfiles, mismas sesiones/navegador en abrir perfil manual y automático, y recuperación de rechecados sin archivos/archivos innecesarios.
3. Developer Twin con sesión de usuario equivalente, diagnóstico por sección y exportación de hallazgos; aislar secretos y listas reales en reportes.
4. Ante clic incierto, journal malformado, protección, challenge o estado no verificable: parada segura sin replay ni contabilizar acciones como éxito.
5. Validación final con cuenta y entorno del propietario explícitamente autorizados; nunca convertir los tests sintéticos en aceptación de Unfollow real.

**Estado:** AUDITADO DOCUMENTALMENTE / RELEASE EN VERIFICACIÓN EN EL CORTE / ACEPTACIÓN REAL DEL ROBOT PENDIENTE. Ver [handoff](CURRENT_HANDOFF.md) y [auditoría central](https://github.com/michels-lab/Michel-Software-Standards/blob/main/reports/2026-10-21_GRANADA_13_REPOS_PLUGIN_AUDIT.md).
