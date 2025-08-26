import time
import os
from botcity.maestro import BotMaestroSDK
from Sic_Login import main as sic_login
from Sic_Modulo_Contabil import main as Sic_Modulo_Contabil
from dotenv import load_dotenv
from bot_logger import get_logger

BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    # Configura logger
    logger = get_logger("sic_orchestrator")
    
    # Carrega variáveis do .env
    load_dotenv()
    
    # Verifica se está sendo executado pelo orquestrador web
    execution_id = os.getenv('RPA_EXECUTION_ID')
    if execution_id:
        logger.set_execution_id(int(execution_id))
        logger.info(f"Execução iniciada via orquestrador web - ID: {execution_id}")

    try:
        maestro = BotMaestroSDK.from_sys_args()
        execution = maestro.get_execution()
        
        logger.info(f"Task ID: {execution.task_id}")
        logger.info(f"Task Parameters: {execution.parameters}")

        # Etapa 1: Login no SIC
        logger.step("Login no SIC", "Iniciando processo de autenticação")
        sic_login()
        logger.success("Login no SIC concluído")

        # Etapa 2: Acessar Modulo Contabil Fiscal
        logger.step("Módulo Contábil", "Acessando funcionalidades fiscais")
        Sic_Modulo_Contabil()
        logger.success("Acesso ao módulo contábil concluído")
        
        logger.success("Processo completo executado com sucesso")
        
    except Exception as e:
        logger.failure(f"Erro durante execução: {str(e)}")
        raise


if __name__ == '__main__':
    main()
