@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo ============================================================
echo   DC DISTRIBUIDORA - DASHBOARD GERENCIAL
echo ============================================================
echo.
echo Pasta atual: %cd%
echo.
echo Conteudo da pasta:
dir /b
echo.

REM Procura requirements.txt (atual ou subpasta dc_dashboard)
if exist "requirements.txt" goto OK
if exist "dc_dashboard\requirements.txt" (
    cd /d "%~dp0\dc_dashboard"
    echo Mudou para subpasta dc_dashboard
    goto OK
)
echo.
echo [ERRO] requirements.txt nao encontrado.
echo Coloque este .bat na mesma pasta de app.py e requirements.txt
echo.
pause
exit /b 1

:OK
echo Arquivos OK. Verificando Python...
where python
if errorlevel 1 (
    echo.
    echo [ERRO] Python nao encontrado no PATH.
    echo Baixe em https://www.python.org/downloads/
    echo Durante a instalacao MARQUE: "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo.

if not exist ".venv" (
    echo [1/3] Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar venv. Verifique permissao da pasta.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Ambiente virtual existente - OK
)

echo.
echo [2/3] Instalando dependencias (pode demorar 1-2 min na primeira vez)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias.
    echo Verifique conexao com a internet.
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando o dashboard...
echo ============================================================
echo   O navegador abrira automaticamente em http://localhost:8501
echo   Para encerrar: feche esta janela ou pressione Ctrl+C
echo ============================================================
echo.
streamlit run app.py
pause
