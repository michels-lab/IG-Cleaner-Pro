# Granada — supervisor de dos cuentas con ejecución simultánea **offline**

**2026-10-30**. Este bloque depende del PR #290 (fábrica opcional de reserva para `ActionRobot`). **No hay nuevos clics ni permisos en Windows**.

Se añade a `DualActionWorkspaces` el parámetro interno `offline_test_runner=None`. En `build_server()`, como siempre, no se pasa: el supervisor normal mantiene `ScopedActionLease` y rechaza ejecutar una segunda tarea de mutación mientras la primera esté viva. No se añade endpoint, botón, setting ni selector que altere esa política.

Sólo cuando un test inyecta un callback `offline_test_runner`, se sustituyen completamente los métodos `_run()` que abrirían Chrome y harían clics. Ambos `ActionRobot.start()` siguen ejecutando la verificación de cuenta/handle/tanda/protegidos y consiguen su reserva individual mediante `SharedGlobalActionCohort.lease`. El coordinador conserva el antiguo mutex global del kernel mientras cualquiera de ambos trabaja.

## Pruebas de aceptación

- Configurar dos @handles distintos bajo el mismo propietario y arrancar dos instancias reales de `ActionRobot` con cuerpos **sin Playwright**.
- Estado de ambos workers independiente; la respuesta reporta inequívocamente `parallel_mutations_enabled:false`.
- Pausar A sólo cancela A; B sigue trabajando y ningún proceso legado puede adquirir el global.
- Pausar B libera el global; reiniciar sin residuos permitido.
- Intentar iniciar la misma cuenta dos veces, cambiar propietario o reconfigurar con workers activos falla sin sustituir cohortes.
- Perfil protegido en B bloquea la tarea, conserva la protección y no cancela A.
- Una llamada real a `build_server(...)` verifica que **la aplicación de producción NO recibe** el callback ni el coordinador de pruebas.
- CI obligatorio en Ubuntu general, Profile Counts y Windows Setup.

## Lo pendiente

El modo simultáneo todavía se limita al harness de tests. El siguiente bloque deberá implementar la ruta de negocio real con consentimiento independiente, doble login verificado en dos Chrome, separación de timers/pacing y pruebas de resultado/clic incierto entre procesos/crashes. No publicar, no habilitar dos Unfollow o Cancel Pending a la vez y mantener issues #164/#176 abiertos.
