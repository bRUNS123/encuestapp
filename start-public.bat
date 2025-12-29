@echo off
echo ========================================
echo   DECIDELIBRE - Modo Publico (ngrok)
echo ========================================
echo.

REM Ruta de ngrok
set NGROK_PATH=C:\Users\bRUNS\Desktop\ngrok-v3-stable-windows-amd64\ngrok.exe

REM Verificar si ngrok existe en la ruta especificada
if not exist "%NGROK_PATH%" (
    echo ERROR: ngrok no encontrado en: %NGROK_PATH%
    echo.
    echo Por favor verifica la ruta de ngrok
    echo.
    pause
    exit /b 1
)

echo Usando ngrok desde: %NGROK_PATH%
echo.

REM Iniciar Backend Django
echo [1/3] Iniciando Backend Django...
start "Django Backend" cmd /k "cd /d d:\PROGRAMACION\decidelibre-gravity\backend && python manage.py runserver 0.0.0.0:8000"

REM Esperar a que Django inicie
echo Esperando a que Django inicie...
timeout /t 8 /nobreak > nul

REM Iniciar ngrok para exponer el backend
echo [2/3] Iniciando ngrok para Backend...
start "ngrok Backend" cmd /k ""%NGROK_PATH%" http 8000 --log=stdout"

REM Esperar a que ngrok inicie
echo Esperando a que ngrok inicie...
timeout /t 5 /nobreak > nul

REM Construir el frontend para producción
echo [3/3] Construyendo Frontend...
cd /d d:\PROGRAMACION\decidelibre-gravity\web-app
call npm run build
cd /d d:\PROGRAMACION\decidelibre-gravity

echo.
echo ========================================
echo   IMPORTANTE - Configuracion ngrok
echo ========================================
echo.
echo 1. Abre la ventana "ngrok Backend"
echo 2. Copia la URL https://XXXX.ngrok-free.app
echo 3. Tus amigos deben acceder a esa URL
echo.
echo NOTA: El frontend ya esta servido por Django
echo desde el backend en la URL de ngrok
echo.
echo Backend (local):  http://localhost:8000
echo Backend (publico): Revisa la ventana ngrok
echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
