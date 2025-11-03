import time
import os
import sqlite3
from botcity.core import DesktopBot
from bot_logger import get_logger

def get_pending_nfs():
    """Busca todas as NFs com status pendente no banco de dados"""
    logger = get_logger("sic_inserir_nf")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'rpa_logs.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, pedido_compra, nota_fiscal, chave_acesso 
            FROM recebimento_nf 
            WHERE status = 'pendente'
            ORDER BY created_at ASC
        """)
        
        nfs = cursor.fetchall()
        conn.close()
        
        logger.info(f"📋 Encontradas {len(nfs)} notas fiscais pendentes para processar")
        return nfs
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar NFs pendentes: {str(e)}")
        return []

def update_nf_status(nf_id, status, error_message=None):
    """Atualiza o status de uma NF no banco de dados"""
    logger = get_logger("sic_inserir_nf")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'rpa_logs.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if error_message:
            cursor.execute("""
                UPDATE recebimento_nf 
                SET status = ?, error_message = ?
                WHERE id = ?
            """, (status, error_message, nf_id))
        else:
            cursor.execute("""
                UPDATE recebimento_nf 
                SET status = ?
                WHERE id = ?
            """, (status, nf_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Status da NF #{nf_id} atualizado para: {status}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar status da NF #{nf_id}: {str(e)}")

def inserir_nf_no_sistema(bot, pedido_compra, nota_fiscal, chave_acesso):
    """Insere uma nota fiscal no sistema SIC"""
    logger = get_logger("sic_inserir_nf")
    
    try:
        logger.step("Adicionar NF", f"PC: {pedido_compra}, NF: {nota_fiscal}")
        
        # Clica no ícone de + para inserir NF
        if not bot.find("Adicionar_NF", matching=0.97, waiting_time=10000):
            logger.error("❌ Elemento não encontrado: Adicionar_NF")
            return False
        bot.click()
        time.sleep(1)
        
        # Inserir o pedido de compra, nf e chave
        if not bot.find("Sic_Chave_NF_Label", matching=0.97, waiting_time=10000):
            logger.error("❌ Elemento não encontrado: Sic_Chave_NF_Label")
            return False
        
        logger.info(f"📝 Preenchendo dados - PC: {pedido_compra}")
        bot.paste(pedido_compra)
        bot.tab()
        
        logger.info(f"🔑 Inserindo chave de acesso: {chave_acesso[:10]}...")
        bot.paste(chave_acesso)
        bot.tab()
        
        logger.info(f"📄 Inserindo nota fiscal: {nota_fiscal}")
        bot.paste(nota_fiscal)
        time.sleep(0.5)
        
        # Clica em adicionar NF
        if not bot.find("Sic_Botao_Adicionar_NF", matching=0.97, waiting_time=10000):
            logger.error("❌ Elemento não encontrado: Sic_Botao_Adicionar_NF")
            return False
        
        bot.click()
        logger.success(f"✅ NF {nota_fiscal} inserida com sucesso!")
        time.sleep(2)  # Aguarda confirmação do sistema
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir NF: {str(e)}")
        return False

def main():
    """Processa todas as notas fiscais pendentes"""
    logger = get_logger("sic_inserir_nf")
    
    logger.info("🚀 Iniciando processamento de Notas Fiscais")
    
    # Buscar NFs pendentes
    nfs_pendentes = get_pending_nfs()
    
    if not nfs_pendentes:
        logger.info("ℹ️ Nenhuma nota fiscal pendente encontrada")
        return
    
    # Inicializar o bot
    bot = DesktopBot()
    time.sleep(2)
    
    # Contadores
    processadas = 0
    com_erro = 0
    
    # Processar cada NF
    for nf in nfs_pendentes:
        nf_id, pedido_compra, nota_fiscal, chave_acesso = nf
        
        logger.step("Processando NF", f"ID: {nf_id}, PC: {pedido_compra}, NF: {nota_fiscal}")
        
        try:
            sucesso = inserir_nf_no_sistema(bot, pedido_compra, nota_fiscal, chave_acesso)
            
            if sucesso:
                update_nf_status(nf_id, 'processado')
                processadas += 1
            else:
                update_nf_status(nf_id, 'erro', 'Falha ao inserir NF no sistema')
                com_erro += 1
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar NF #{nf_id}: {str(e)}")
            update_nf_status(nf_id, 'erro', str(e))
            com_erro += 1
    
    # Relatório final
    logger.info("=" * 60)
    logger.success(f"📊 Processamento concluído!")
    logger.info(f"   ✅ Processadas com sucesso: {processadas}")
    logger.info(f"   ❌ Com erro: {com_erro}")
    logger.info(f"   📋 Total: {len(nfs_pendentes)}")
    logger.info("=" * 60)








