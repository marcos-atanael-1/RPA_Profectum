import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

class BotLogger:
    """Sistema de logging integrado para os bots RPA"""
    
    def __init__(self, execution_id=None, db_path='../rpa_logs.db'):
        self.execution_id = execution_id
        self.db_path = db_path
        self.module_name = 'bot'
        
    def set_module(self, module_name):
        """Define o nome do módulo que está gerando os logs"""
        self.module_name = module_name
        
    def set_execution_id(self, execution_id):
        """Define o ID da execução atual"""
        self.execution_id = execution_id
    
    @contextmanager
    def get_db_connection(self):
        """Context manager para conexão com o banco"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except Exception as e:
            print(f"Erro de conexão com BD: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def _log(self, level, message):
        """Método interno para registrar logs"""
        if not self.execution_id:
            print(f"[{level}] {message}")
            return
            
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO bot_log (execution_id, timestamp, level, message, module)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    self.execution_id,
                    datetime.utcnow(),
                    level,
                    message,
                    self.module_name
                ))
                conn.commit()
        except Exception as e:
            print(f"Erro ao salvar log: {e}")
        
        # Também imprime no console
        print(f"[{level}] {message}")
    
    def info(self, message):
        """Log de informação"""
        self._log('INFO', message)
    
    def warning(self, message):
        """Log de aviso"""
        self._log('WARNING', message)
    
    def error(self, message):
        """Log de erro"""
        self._log('ERROR', message)
    
    def debug(self, message):
        """Log de debug"""
        self._log('DEBUG', message)
    
    def step(self, step_name, details=""):
        """Log de etapa do processo"""
        message = f"Executando etapa: {step_name}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def success(self, message):
        """Log de sucesso"""
        self.info(f"✅ {message}")
    
    def failure(self, message):
        """Log de falha"""
        self.error(f"❌ {message}")

# Instância global do logger
logger = BotLogger()

def get_logger(module_name="bot"):
    """Retorna uma instância do logger configurada para o módulo"""
    logger.set_module(module_name)
    return logger 