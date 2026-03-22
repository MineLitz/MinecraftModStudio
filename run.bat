@echo off
title Minecraft Mod Studio
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo  [ERRO] Falha ao iniciar. Execute install.bat primeiro.
    pause
)
