import time
import os
from botcity.core import DesktopBot

def main():
    bot = DesktopBot()
    time.sleep(5)

    # Clica no menu Contabil
    if not bot.find("Sic_Menu_Contabil", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: Sic_Menu_Contabil")
    else:
        bot.click()

    # Clica em romaneio
    if not bot.find("Sic_Menu_Romaneio", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: Sic_Menu_Romaneio")
    else:
        bot.click()
        
    # Searching for element 'Sic_Menu_Fiscal '
    if not bot.find("Sic_Menu_Fiscal", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: Sic_Menu_Fiscal")
    bot.click()
    
