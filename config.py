"""
Configurações do RPA Profectum
Carrega variáveis de ambiente do arquivo .env
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# ========================================
# Flask
# ========================================
SECRET_KEY = os.getenv('SECRET_KEY', 'rpa-profectum-secret-key-2024')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///rpa_logs.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# ========================================
# API Romaneios - Configurações Externas
# ========================================
API_BASE_URL = os.getenv('API_BASE_URL', 'http://172.16.0.17:3600')
API_SYSTEM_ID = os.getenv('API_SYSTEM_ID', 'sys_1f02a9e8b5f24d73b8e74d8fae931c64_prod')

# ========================================
# Modo de Operação
# ========================================
# True = Modo teste (não chama API real), False = Produção (chama API)
MODO_TESTE = os.getenv('MODO_TESTE', 'True').lower() == 'true'

# ========================================
# Verificador Automático de Romaneios
# ========================================
INTERVALO_VERIFICACAO_MINUTOS = int(os.getenv('INTERVALO_VERIFICACAO_MINUTOS', 5))
MAX_TENTATIVAS_CONTAGEM = int(os.getenv('MAX_TENTATIVAS_CONTAGEM', 3))
VERIFICADOR_ATIVO = os.getenv('VERIFICADOR_ATIVO', 'True').lower() == 'true'
VERIFICADOR_LOG_DETALHADO = os.getenv('VERIFICADOR_LOG_DETALHADO', 'True').lower() == 'true'

# ========================================
# Opções Padrão da API de Inserção
# ========================================
API_APOS_RECEBIMENTO = os.getenv('API_APOS_RECEBIMENTO', 'False').lower() == 'true'
API_PROGRAMADO = os.getenv('API_PROGRAMADO', 'True').lower() == 'true'
API_INSERIR_PARCIAL_SE_EXISTIR = os.getenv('API_INSERIR_PARCIAL_SE_EXISTIR', 'False').lower() == 'true'

# ========================================
# Status de Romaneios
# ========================================
STATUS_PENDENTE = 'P'  # Aguardando contagem
STATUS_ABERTO = 'A'    # Quantidades bateram
STATUS_RECEBIDO = 'R'  # Recebido
STATUS_FINALIZADO = 'F' # Finalizado

STATUS_CHOICES = {
    'P': 'Pendente',
    'A': 'Aberto',
    'R': 'Recebido',
    'F': 'Finalizado'
}

STATUS_COLORS = {
    'P': 'warning',   # Amarelo
    'A': 'success',   # Verde
    'R': 'info',      # Azul
    'F': 'secondary'  # Cinza
}

