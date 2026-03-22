@echo off
title Minecraft Mod Studio — Instalador
color 0A

echo.
echo  ==========================================
echo    Minecraft Mod Studio — Instalacao
echo  ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao encontrado!
    echo  Baixe em: https://www.python.org/downloads/
    echo  IMPORTANTE: Marque "Add Python to PATH" durante a instalacao
    echo.
    pause
    exit /b 1
)

echo  [OK] Python encontrado
python --version

echo.
echo  Instalando dependencias...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo  [ERRO] Falha ao instalar dependencias.
    echo  Tente executar como Administrador.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo    Instalacao concluida com sucesso!
echo  ==========================================
echo.
echo  Execute run.bat para iniciar o aplicativo
echo.
pause
