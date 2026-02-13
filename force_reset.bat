@echo off
setlocal
echo ==========================================
echo   LIMPEZA E RESET DO GIT - SALES ANALYTICS
echo ==========================================

REM Tenta encontrar o executavel do Git
where git >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set GIT_CMD=git
) else (
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
    ) else (
        if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe" (
            set "GIT_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe"
        ) else (
            echo [ERRO] Git nao encontrado!
            echo Por favor, instale o Git ou rode este script pelo "Git Bash".
            pause
            exit /b 1
        )
    )
)

echo Usando Git em: "%GIT_CMD%"

echo [1/5] Removendo arquivos temporarios...
del "seed_database.py" 2>nul
del "check_db.py" 2>nul
del "setup_git.bat" 2>nul
del "start_api.bat" 2>nul
del "start_dashboard.bat" 2>nul

echo [2/5] Apagando historico antigo do Git...
if exist ".git" (
    rmdir /s /q .git
)

echo [3/5] Iniciando novo repositorio limpo...
"%GIT_CMD%" init
"%GIT_CMD%" config user.name "Hubbleq"
"%GIT_CMD%" config user.email "bruno.pires23@aluno.unip.br"

echo [4/5] Criando commit unico inicial...
"%GIT_CMD%" add .
"%GIT_CMD%" commit -m "Sales Analytics Pipeline v2.0 - Historico Limpo"

echo [5/5] Configurando repositorio remoto...
"%GIT_CMD%" branch -M main
"%GIT_CMD%" remote add origin https://github.com/Hubbleq/sales-etl.git

echo.
echo ========================================================
echo   TUDO PRONTO LOCAMENTE!
echo   Agora, para atualizar o GitHub e remover o outro usuario,
echo   rode o comando abaixo:
echo.
echo   "%GIT_CMD%" push -f origin main
echo ========================================================
echo.
cmd /k
