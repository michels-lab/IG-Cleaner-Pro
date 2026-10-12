# Automatizaciones — especificación y estado

**Estado 2026-10-12:** panel de planificación y exclusiones implementado en rama de desarrollo. **Ninguna cancelación o unfollow automático se ejecuta aún.** La ejecución necesita un navegador real, verificaciones en la cuenta correcta y pruebas de aceptación antes de publicar.

## Límites de producto

- **Mutuals** solo usa **Focos de revisión** (20/30/40); no tiene automatizaciones ni cambios de relación por robot. Para priorizar el Focus se añade la proporción Following/Followers *de cada perfil* solo cuando Profile Counts tiene ambas cifras con estado válido. Un cociente alto puede subir la prioridad de revisión, nunca autoriza unfollow ni implica fraude.
- **Automatizaciones** es un workspace separado con futuras tareas de cancelar solicitudes enviadas y dejar de seguir cuentas que no siguen de vuelta. Usa archivos y sesión visibles de Chrome local, no Meta Graph API; no solicita contraseñas de Instagram en la app.
- **Omitir esta vez:** excluye la entrada del lote de planificación actual; **Nueva tanda** limpia estas omisiones temporales.
- **★ Proteger / Favorito:** exclusión persistente por usuario de IG Cleaner e Instagram seleccionado, accesible desde **Perfiles protegidos**. Unfollow aprovecha también el set existente de protegidos de Review y Mutuals; los protegidos nunca deben ejecutarse.
- **Tiempos:** tamaño de tanda, descanso entre tandas y segundos entre perfiles pueden guardarse por perfil y tarea. No son una ejecución activa mientras el backend de acciones siga pendiente.

## Requisitos antes de activar acciones reales

1. Cola explícita verificada a partir del Instagram seleccionado; no asumir que la ausencia en un archivo parcial demuestra falta de followback.
2. Confirmación de usuario por tipo, conteo y perfiles antes de comenzar la primera tanda; deduplicación e idempotencia por cuenta y tipo de acción.
3. Verificación del nombre visible y del estado del botón **en el perfil actual** antes de cambiar una relación; nada de clics ciegos ni botones por posición fija.
4. Ante desafíos, CAPTCHA, login, cambio de cuenta, ausencia de controles, cancelación, límite de plataforma o error, **detener**, mostrar causa y conservar avance; no eludir restricciones ni reintentar agresivamente.
5. Pausar y Reanudar deben guardar registros auditables por perfil: pendiente / ejecutado / omitido / protegido / fallido, con fecha y método. No tomar un clic como éxito sin verificar estado posterior.
6. Respeto estricto a la misma identidad del app-login e Instagram, sin cambios de cuenta tácitos, ni reutilizar acciones en otra sesión.
7. Pruebas unitarias con DOM sintético, navegador real con cuentas controladas (incluida confirmación y desafío), pruebas de controles en compact/desktop, regresión de Focus y protección persistente.
8. Publicar solo después de CI verde y autorización de release. Probar en cuenta real puede provocar límites de Instagram; no hay garantía de disponibilidad.

Los exports y resultados siguen siendo locales. No se debe enviar la contraseña de Instagram ni cookies a Supabase.
