import time
import os
from botcity.core import DesktopBot

def main():
    bot = DesktopBot()
    time.sleep(5)
    
    # Executa o sistema
    bot.execute(r"C:\Users\marcosatanael\Desktop\SIC - Teste\SIC - Sistema Integrado Cerbras.exe")
    time.sleep(5)

    # Pega usuário e senha do .env
    usuario = os.getenv("SIC_USUARIO")
    senha = os.getenv("SIC_SENHA")

    # Preenche usuário
    if not bot.find("sic_usuario", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: sic_usuario")
    else:
        bot.click()
        bot.paste(usuario)
        bot.tab()
        bot.paste(senha)

    # Clica em logar
    if not bot.find("Sic_logar", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: Sic_logar")
    else:
        bot.click()
