@echo off
cd /d "%~dp0"
echo ===========================================
echo   SALES ANALYTICS - INICIANDO SISTEMA
echo ===========================================

echo [1/3] Fechando processos antigos nas portas 8000 e 8501...
:: Procura por processos escutando nas portas (Ingles e Portugues)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| findstr /i "LISTENING OUVINDO ESCUTANDO"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8501" ^| findstr /i "LISTENING OUVINDO ESCUTANDO"') do taskkill /f /pid %%a >nul 2>&1

:: Garante que nao sobrou nenhum uvicorn ou streamlit perdido
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM streamlit.exe >nul 2>&1

echo [2/3] Iniciando API (Backend)...
start "API - Sales Analytics" cmd /k .venv\Scripts\python.exe -m uvicorn app.api.main:app --reload --port 8001

echo [3/3] Iniciando Dashboard (Frontend)...
timeout /t 5 >nul
start "Dashboard - Sales Analytics" cmd /k .venv\Scripts\streamlit.exe run dashboard\streamlit_app.py --server.port 8501

echo.
echo ===========================================
echo   SISTEMA INICIADO!
echo   API: http://localhost:8001
echo   Dashboard: http://localhost:8501
echo ===========================================
echo.
pause
