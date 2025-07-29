import time
from botcity.maestro import BotMaestroSDK
from Sic_Login import main as sic_login
from Sic_Modulo_Contabil import main as Sic_Modulo_Contabil
from dotenv import load_dotenv

BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    # Carrega variáveis do .env
    load_dotenv()

    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()
    
    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    # Etapa 1: Login no SIC
    sic_login()

    # Etapa 2: Acessar Modulo Contabil Fiscal
    Sic_Modulo_Contabil()


if __name__ == '__main__':
    main()
