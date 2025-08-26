
#!/usr/bin/env python3
"""
Script de inicialização do RPA Profectum Orquestrador
Este script configura e inicia a interface web para gerenciar automações RPA
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        ('flask', 'flask'),
        ('flask_sqlalchemy', 'flask-sqlalchemy'),
        ('dotenv', 'python-dotenv'),
        ('requests', 'requests'),
        ('flask_login', 'flask-login')
    ]
    
    missing = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"❌ Dependências faltando: {', '.join(missing)}")
        print("💡 Instale com: pip install -r requirements_web.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def setup_environment():
    """Configura o ambiente"""
    print("⚙️ Configurando ambiente...")
    
    # Verifica se existe arquivo .env para os bots
    env_path = Path("entrada-nf/.env")
    if not env_path.exists():
        print("⚠️ Arquivo .env não encontrado em entrada-nf/")
        print("📝 Criando arquivo .env de exemplo...")
        
        env_content = """# Configurações do Sistema SIC
SIC_USUARIO=seu_usuario_sic
SIC_SENHA=sua_senha_sic

# Configurações do Sistema RM
RM_USUARIO=seu_usuario_rm
RM_SENHA=sua_senha_rm

# Configurações do Orquestrador
RPA_EXECUTION_ID=
"""
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Arquivo .env criado em {env_path}")
        print("📋 Configure suas credenciais no arquivo .env antes de executar os bots")
    
    # Verifica se existe o diretório de templates
    templates_dir = Path("templates")
    if not templates_dir.exists():
        print("❌ Diretório de templates não encontrado")
        return False
    
    print("✅ Ambiente configurado")
    return True

def start_server():
    """Inicia o servidor Flask"""
    print("\n🚀 Iniciando RPA Profectum Orquestrador...")
    print("=" * 50)
    print("🌐 Interface Web: http://localhost:5000")
    print("🔐 Login: http://localhost:5000/login")
    print("📊 Dashboard: http://localhost:5000/")
    print("🤖 Gerenciar Bots: http://localhost:5000/bots")
    print("📋 Logs: http://localhost:5000/logs")
    print("👥 Usuários: http://localhost:5000/users")
    print("=" * 50)
    print("🔑 Login Padrão:")
    print("   Usuário: profectum")
    print("   Senha: 123456")
    print("=" * 50)
    print("💡 Pressione Ctrl+C para parar o servidor")
    print()
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def show_help():
    """Mostra informações de ajuda"""
    help_text = """
🤖 RPA Profectum Orquestrador

Este orquestrador web permite:
• 📊 Dashboard com estatísticas das automações
• 🎮 Execução e monitoramento de bots em tempo real
• 📋 Visualização detalhada de logs
• 🗃️ Persistência de dados em SQLite
• 🔄 Auto-refresh e atualizações em tempo real

Bots Disponíveis:
• SIC - Processo Completo: Login + Módulo Contábil/Fiscal
• SIC - Apenas Login: Autenticação no sistema SIC
• RM - Login: Autenticação no sistema TOTVS RM
• Consulta NFe: Validação de notas fiscais via API

Estrutura do Projeto:
├── app.py                    # Aplicação Flask principal
├── templates/               # Templates HTML
├── entrada-nf/             # Bots RPA existentes
│   ├── bot.py              # Bot principal (SIC)
│   ├── bot_logger.py       # Sistema de logging
│   └── .env                # Configurações
└── rpa_logs.db            # Banco de dados SQLite

Para configurar:
1. Configure suas credenciais em entrada-nf/.env
2. Execute: python start_rpa_orchestrator.py
3. Acesse: http://localhost:5000

Suporte: Este é um sistema de demonstração para automações RPA.
"""
    print(help_text)

def main():
    """Função principal"""
    print("🤖 RPA Profectum - Orquestrador de Automações")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        return
    
    # Verificações preliminares
    if not check_requirements():
        sys.exit(1)
    
    if not setup_environment():
        sys.exit(1)
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main() 