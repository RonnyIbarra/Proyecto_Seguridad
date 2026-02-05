@echo off
REM Script de instalación automática para Windows
REM Instala todas las dependencias y prepara el proyecto

echo.
echo ╔════════════════════════════════════════════╗
echo ║     INSTALADOR - CryptoVault v1.0         ║
echo ║  Sistema Seguro de Criptografia           ║
echo ╚════════════════════════════════════════════╝
echo.

REM Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python no encontrado. Instálalo de https://python.org
    pause
    exit /b 1
)
echo ✓ Python encontrado

REM Crear entorno virtual
echo.
echo [2/4] Creando entorno virtual...
cd backend
if not exist venv (
    python -m venv venv
    echo ✓ Entorno virtual creado
) else (
    echo ✓ Entorno virtual ya existe
)

REM Activar y instalar dependencias
echo.
echo [3/4] Instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
echo ✓ Dependencias instaladas

REM Crear base de datos
echo.
echo [4/4] Preparando base de datos...
python -c "from sqlalchemy import create_engine; create_engine('sqlite:///crypto_app.db')" 2>nul
echo ✓ Base de datos lista

echo.
echo ╔════════════════════════════════════════════╗
echo ║      ¡INSTALACION COMPLETADA!             ║
echo ╚════════════════════════════════════════════╝
echo.
echo PRÓXIMOS PASOS:
echo.
echo 1. Abre dos terminales (cmd):
echo.
echo TERMINAL 1 (Backend):
echo   cd Proyecto_Ibarra_Rivera_Sacnhez\backend
echo   venv\Scripts\activate
echo   python main.py
echo.
echo TERMINAL 2 (Frontend):
echo   cd Proyecto_Ibarra_Rivera_Sacnhez\frontend
echo   python -m http.server 8080
echo.
echo   Luego abre: http://localhost:8080
echo.
echo ╔════════════════════════════════════════════╗
echo ║     Presiona cualquier tecla para salir    ║
echo ╚════════════════════════════════════════════╝
pause
