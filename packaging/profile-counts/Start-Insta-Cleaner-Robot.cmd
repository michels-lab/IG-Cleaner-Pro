@echo off
setlocal
cd /d "%~dp0"
title Michel's Lab - Insta Cleaner - Profile Counts
if not exist "%~dp0IGCleanerProfileCounts.exe" (
  echo [ERROR] Falta IGCleanerProfileCounts.exe en esta carpeta.
  echo Descarga el paquete completo; no copies solo el lanzador.
  pause
  exit /b 1
)
if not exist "%~dp0IG-Cleaner-Pro.html" (
  echo [ERROR] Falta IG-Cleaner-Pro.html en esta carpeta.
  echo Descarga el paquete completo. No borres la base de datos ni los respaldos.
  pause
  exit /b 1
)
echo.
echo Michel's Lab - Insta Cleaner Pro
echo Profile Counts - Navegador local visible
echo.
echo IMPORTANTE: Si cambias de navegador o de ruta del HTML,
echo es posible que cambie el almacenamiento local del workspace.
echo Cierra esta ventana para detener el puente.
echo.
"%~dp0IGCleanerProfileCounts.exe" --app "%~dp0IG-Cleaner-Pro.html"
if errorlevel 1 (
  echo.
  echo [ERROR] El robot no inicio. Necesitas Google Chrome instalado en Windows.
  echo Verifica tambien que el antivirus permita ejecutar el archivo.
  pause
  exit /b 1
)
endlocal
