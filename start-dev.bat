@echo off
echo ========================================
echo   DECIDELIBRE - Iniciando Desarrollo
echo ========================================
echo.

REM Iniciar Backend Django en una nueva ventana
echo [1/2] Iniciando Backend Django...
start "Django Backend" cmd /k "cd backend && python manage.py runserver 0.0.0.0:8000"

REM Esperar 3 segundos para que Django inicie
timeout /t 3 /nobreak > nul

REM Iniciar Frontend Vite en una nueva ventana
echo [2/2] Iniciando Frontend Vite...
start "Vite Frontend" cmd /k "cd web-app && npm run dev"

echo.
echo ========================================
echo   Servidores iniciados exitosamente!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause > nul
