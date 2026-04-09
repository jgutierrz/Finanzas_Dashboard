@echo off

cd /d "D:\G751JT\PERSONAL\Python\Finanzas Dashboard"

call venv\Scripts\activate

echo =========================
echo ACTUALIZANDO DATOS
echo =========================

python -m scripts.update_data

echo ESPERANDO 3 SEGUNDOS...
timeout /t 3

echo =========================
echo INICIANDO STREAMLIT...
echo =========================

start cmd /k streamlit run app/app.py