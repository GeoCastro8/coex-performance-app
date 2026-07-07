@echo off
echo Iniciando Servidor de Aplicacion de Coextruido...
cd /d "%~dp0"
call venv\Scripts\activate
streamlit run app.py
pause
