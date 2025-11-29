@echo off
REM run_all.bat - Windows (CMD)
SETLOCAL

REM Activar venv (Windows CMD)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo No se encontro venv\Scripts\activate.bat. Asegurate de haber creado el entorno virtual.
    pause
    exit /b 1
)

echo Ejecutando run_all.py con el python del venv...
python run_all.py
SET EXIT_CODE=%ERRORLEVEL%

echo run_all finalizo con codigo %EXIT_CODE%.
ENDLOCAL
exit /b %EXIT_CODE%
