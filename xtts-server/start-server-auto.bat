@echo off
REM Iniciar servidor automaticamente respondendo "Nao" aos prompts de CUDA
cd /d "%~dp0"
(
  echo 2
) | call start-server.bat
