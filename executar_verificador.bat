@echo off
REM ========================================
REM Script para Agendador de Tarefas
REM Executa verificador de romaneios
REM ========================================

cd /d "C:\Users\Marcos\Desktop\RPA_Profectum"

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Executar verificador uma vez
python verificador_romaneios.py --once

REM Desativar ambiente virtual
call venv\Scripts\deactivate.bat

exit

