import time
import os
from botcity.core import DesktopBot

def main():

    pedidocompra = '12345'
    notafiscal = '3453'
    chave = 'asdadasfasdfsfa'


    bot = DesktopBot()
    time.sleep(5)

    # Clica no icone de + para inserir NF
    if not bot.find("Adicionar_NF", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: Adicionar_NF")
    else:
        bot.click()

    # Inserir a pedido de compra, nf e chave
    if not bot.find("Sic_Chave_NF_Label", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: Sic_Chave_NF_Label")
    else:
        bot.paste(pedidocompra)
        bot.tab()
        bot.paste(chave)
        bot.tab()
        bot.paste(notafiscal)

    # Clica em adicionar NF
    if not bot.find("Sic_Botao_Adicionar_NF", matching=0.97, waiting_time=10000):
        print("Elemento não encontrado: Sic_Botao_Adicionar_NF")
    else:
        bot.click()








