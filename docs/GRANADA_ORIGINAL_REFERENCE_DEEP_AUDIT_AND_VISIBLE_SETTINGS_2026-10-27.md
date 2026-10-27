# GRANADA — auditoría profunda del código original y descubribilidad de ajustes (2026-10-27)

## Archivo de referencia recuperado

El usuario compartió previamente `Pasted text(3).txt`, bundle JavaScript/React/Webpack minificado de aproximadamente **149 KB**. Se logró consultar su contenido textual original disponible en los archivos de la conversación/proyecto; **no hace falta solicitarlo de nuevo**, salvo que el propietario tenga otra revisión más reciente. **No se copió el bundle** al repositorio.

### Cómo trabaja realmente la referencia

- El módulo de constantes usa `DEFAULT_USERS_PER_SEARCH_CYCLE = 50`, `DEFAULT_TIME_BETWEEN_SEARCH_CYCLES = 1000 ms`, `DEFAULT_TIME_TO_WAIT_AFTER_FIVE_SEARCH_CYCLES = 10000 ms` y `CHECKS_BEFORE_LONG_SLEEP = 15`. El rótulo del ajuste menciona "after five" aunque el código de búsqueda acumula 15 ciclos antes de su descanso extendido: **las etiquetas no prueban el intervalo real**.
- El formulario de Settings expone **cinco controles guardados** (`iu_timings`): tiempo entre ciclos de lectura, tiempo de descanso extendido, tiempo entre unfollows, descanso tras varios unfollows y usuarios por petición. Mezcla lector y acciones; InstaCleaner mantiene ambos sistemas estrictamente separados.
- La solicitud real para la lista usa el ID del propietario de sesión y `/api/v1/friendships/{id}/{following|followers}/?count=…&max_id=…`, con datos de múltiples usuarios por página, no navegación a cada perfil. Una rutina adicional puede buscar un username concreto en Following para verificar un objetivo, pero **esa verificación puntual no es el algoritmo de obtención masiva**.
- El script introduce fluctuaciones temporales de cientos de milisegundos, además de un intervalo dependiente de las preferencias, y descansos más largos después de un número de ciclos. Tiene un tope de 250 páginas en esa compilación.
- En determinadas respuestas de bloqueo o red, el código de ejemplo usa reintentos y esperas crecientes desde **30 segundos**. InstaCleaner **no debe copiar** esa política de reintentos cuando Instagram responde con 429/403/`feedback_required`; la app suspende lecturas, respeta `Retry-After` y conserva el enfriamiento. La seguridad no se garantiza usando un temporizador.

### Diferencias en InstaCleaner después de #274

- [PR #274](https://github.com/michels-lab/IG-Cleaner-Pro/pull/274), ya integrado, crea backend `tools/live_scan_settings.py` con perfiles **Recomendado, Más pausado, Personalizado** y siete controles guardados **por login y workspace de Instagram**. El motor valida todos los límites y mantiene inmutable una configuración por escaneo. Nunca aplica tiempos de listas al robot de Unfollow.
- Ajustes Recomendado del motor actual: solicita hasta **200 personas por página JSON**, **2.5 s entre páginas**, **12 s de descanso cada 5** páginas, **90 s cada 25** y **15 min entre escaneos completados**. El perfil Más pausado utiliza 100/página, 5 s, 25 s cada cinco, 180 s cada veinte y 30 min entre escaneos. Estos valores son *predeterminados propios de la app*, no cotas oficiales de Instagram.
- Las barreras irrenunciables continúan: identidad exacta de cuenta, GET de listas en Chrome autenticado, sin visitas individuales para recolectar membresía, no Unfollow, parar ante 429/403/503/desafío/`feedback_required`, cooldown persistente del mismo Chrome, resultados incompletos rechazados y snapshot anterior preservado.

## Problema funcional de descubrimiento aún pendiente

La versión **v120.70 publicada** precede a la integración del panel de ajustes de #274. Incluso en ese código posterior, la sección `<details id="igcLiveSettingsPanel">` inicialmente estaba **cerrada**, y cambiar de workspace con ese panel abierto no garantizaba recarga previa de los valores visibles antes de empezar una lectura. Un usuario podía creer que solo existían los tres botones Verify/Stop/Last snapshot.

### Correcciones fuente de esta rama

1. El panel aparece **abierto de entrada** en Automations y conserva la opción de plegarse; muestra explícitamente `Recomendado (predeterminado)`, los siete valores con unidades y los perfiles disponibles.
2. Se incorpora una línea visible `Perfil mostrado …` para distinguir ajustes cargados y borradores pendientes de guardar, y botón **Recargar ajustes de esta cuenta**.
3. Cuando cambia la cuenta, la vista activa intenta recargar la configuración persistida. Al pulsar Verify, antes de confirmar la lectura se verifica que el UI haya cargado la configuración guardada **del mismo owner y workspace**; si el puente no la puede verificar, detiene el inicio sin tocar Instagram.
4. El backend continúa siendo la autoridad: los presets y las preferencias custom requieren validación numérica dentro de límites protectores; la app deshabilita edición durante una lectura y no modifica valores ya capturados por ese escaneo.
5. Se fortalecen los tests `tests/test_live_scan_settings.py` para exigir panel abierto, perfil visible, botón recarga y comprobación de coincidencia antes de empezar.

## Validaciones que no pueden reclamarse

No se ha ejecutado ninguna consulta real a los seguidores del usuario ni se ha observado una reducción real de bloqueos de Instagram; las APIs privadas de Instagram pueden cambiar o restringir la sesión. Esta rama **no está en el instalador oficial v120.70**. Cualquier publicación necesita **versión nueva normal FINAL**, pruebas del ejecutable instalado, Android public/Developer y QA visual exacta, y nunca RC/beta. Ningún script de la referencia se copió íntegramente.
