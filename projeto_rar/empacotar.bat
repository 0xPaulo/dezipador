@echo off
REM Ativa o ambiente virtual
call env\Scripts\activate.bat

REM Empacota o app com PyInstaller
pyinstaller --add-data "icon.ico;." --onefile --windowed --icon=icon.ico --version-file=version.txt codigo5.py

REM Espera uma tecla para encerrar
echo.
echo Aplicativo empacotado! Pressione qualquer tecla para sair...
pause >nul
