#!/usr/bin/env python3
"""
Script de migração para criar a tabela recebimento_nf
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path para importar o app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, RecebimentoNF

def create_recebimento_nf_table():
    """Cria a tabela recebimento_nf no banco de dados"""
    
    print("🔄 Iniciando migração da tabela recebimento_nf...")
    
    with app.app_context():
        try:
            # Verificar se a tabela já existe
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'recebimento_nf' in existing_tables:
                print("✅ Tabela 'recebimento_nf' já existe no banco de dados.")
                return True
            
            # Criar a tabela
            print("📝 Criando tabela 'recebimento_nf'...")
            db.create_all()
            
            # Verificar se a tabela foi criada
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'recebimento_nf' in existing_tables:
                print("✅ Tabela 'recebimento_nf' criada com sucesso!")
                
                # Mostrar estrutura da tabela
                columns = inspector.get_columns('recebimento_nf')
                print("\n📋 Estrutura da tabela:")
                for column in columns:
                    print(f"   - {column['name']}: {column['type']}")
                
                return True
            else:
                print("❌ Erro: Tabela não foi criada.")
                return False
                
        except Exception as e:
            print(f"❌ Erro durante a migração: {str(e)}")
            return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 MIGRAÇÃO DO BANCO DE DADOS - RPA Profectum")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📁 Diretório: {os.getcwd()}")
    print()
    
    # Verificar se o arquivo do banco existe
    db_path = os.path.join('instance', 'rpa_logs.db')
    if os.path.exists(db_path):
        print(f"✅ Banco de dados encontrado: {db_path}")
    else:
        print(f"⚠️  Banco de dados não encontrado: {db_path}")
        print("   O banco será criado automaticamente.")
    
    print()
    
    # Executar migração
    success = create_recebimento_nf_table()
    
    print()
    print("=" * 60)
    if success:
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("   Agora você pode acessar a página de Recebimento NF.")
    else:
        print("❌ MIGRAÇÃO FALHOU!")
        print("   Verifique os erros acima e tente novamente.")
    print("=" * 60)

if __name__ == "__main__":
    main()