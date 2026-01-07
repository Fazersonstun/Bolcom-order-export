@echo off
setlocal

cd /d C:\dev\bol-agent

REM Ensure correct module path
set PYTHONPATH=%cd%\src

REM Activate venv
call .venv\Scripts\activate.bat

REM Ensure folders exist
if not exist logs mkdir logs
if not exist data\exports mkdir data\exports
if not exist data\state mkdir data\state

REM Run + log output
python -u -m bol_agent.run_export >> logs\run.log 2>&1

endlocal
