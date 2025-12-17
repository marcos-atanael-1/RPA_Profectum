"""
Script de migração para adicionar tabelas de Romaneios
Mantém todas as tabelas existentes (user, bot_execution, bot_log, system_settings, recebimento_nf)
"""
import sys
from datetime import datetime
from app import app, db, Romaneio, RomaneioItem, RomaneioLog

def migrate():
    """Executa a migração do banco de dados"""
    print("=" * 60)
    print("MIGRACAO DO BANCO DE DADOS - ROMANEIOS")
    print("=" * 60)
    
    with app.app_context():
        print("\n[1/4] Verificando tabelas existentes...")
        
        # Importar User para garantir que a referência funcione
        from app import User
        
        # Verificar se as tabelas de romaneio já existem
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"   Tabelas atuais no banco: {', '.join(existing_tables)}")
        
        romaneio_tables = ['romaneio', 'romaneio_item', 'romaneio_log']
        tables_to_create = [t for t in romaneio_tables if t not in existing_tables]
        
        if not tables_to_create:
            print("\n   AVISO: Todas as tabelas de romaneio ja existem!")
            resposta = input("\n   Deseja recriar as tabelas? (ISSO APAGARA OS DADOS) [s/N]: ")
            if resposta.lower() != 's':
                print("\n   Migracao cancelada.")
                return
            
            print("\n[2/4] Removendo tabelas de romaneio existentes...")
            Romaneio.__table__.drop(db.engine, checkfirst=True)
            RomaneioItem.__table__.drop(db.engine, checkfirst=True)
            RomaneioLog.__table__.drop(db.engine, checkfirst=True)
            print("   Tabelas removidas com sucesso!")
        else:
            print(f"\n[2/4] Tabelas a serem criadas: {', '.join(tables_to_create)}")
        
        print("\n[3/4] Criando novas tabelas de romaneio...")
        
        # Criar apenas as tabelas de romaneio
        Romaneio.__table__.create(db.engine, checkfirst=True)
        print("   - Tabela 'romaneio' criada")
        
        RomaneioItem.__table__.create(db.engine, checkfirst=True)
        print("   - Tabela 'romaneio_item' criada")
        
        RomaneioLog.__table__.create(db.engine, checkfirst=True)
        print("   - Tabela 'romaneio_log' criada")
        
        print("\n[4/4] Verificando estrutura final...")
        inspector = db.inspect(db.engine)
        final_tables = inspector.get_table_names()
        print(f"   Tabelas no banco: {', '.join(final_tables)}")
        
        print("\n" + "=" * 60)
        print("MIGRACAO CONCLUIDA COM SUCESSO!")
        print("=" * 60)
        print("\nProximos passos:")
        print("1. Iniciar o servidor: python app.py")
        print("2. Acessar: http://localhost:5000/romaneios")
        print("3. Criar romaneios e testar o sistema")
        print("\n")

if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"\nERRO durante a migracao: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

