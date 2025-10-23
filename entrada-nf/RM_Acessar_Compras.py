
import time
import os
from botcity.core import DesktopBot

def main():
    time.sleep(5)
    bot = DesktopBot()
    time.sleep(3)


    # Searching for element 'RM_Menu_Compras '
    if not bot.find("RM_Menu_Compras", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: RM_Menu_Compras")
    bot.click()


    # Clica no menu compras RM
    if not bot.find("RM_Botao_Recebimento", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: RM_Botao_Recebimento")
    else:
        bot.click()

    # Searching for element 'RM_Tipo_Movimento_Imput '
    if not bot.find("RM_Tipo_Movimento_Imput", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: RM_Tipo_Movimento_Imput")
    bot.paste('1216')
    bot.tab()
    bot.tab()
    bot.tab()
    bot.tab()
    bot.tab()
    bot.tab()
    bot.enter()











