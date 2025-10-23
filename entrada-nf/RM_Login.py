import time
import os
from botcity.core import DesktopBot

def main():
    bot = DesktopBot()
    time.sleep(5)
    
    # Executa o sistema
    bot.execute(r"C:\totvs\CorporeRM\RM.Net\RM.exe")
    time.sleep(5)

    # Pega usuário e senha do .env
    usuario = os.getenv("RM_USUARIO")
    senha = os.getenv("RM_SENHA")

# Searching for element 'RM_Ususario_icon '
    #if not bot.find("RM_Ususario_icon", matching=0.97, waiting_time=10000):
        #print("Elemento não encontrado: RM_Ususario_icon")
    #bot.click_relative(54, 13)
    #bot.paste(usuario)
    
    
   # Searching for element 'RM_Senha_Icon '
    if not bot.find("RM_Senha_Icon", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: RM_Senha_Icon")
    bot.click_relative(46, 16)
    bot.paste(senha)


    if not bot.find("RM_Logar", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: RM_Logar")
    bot.click()
    
    

main()