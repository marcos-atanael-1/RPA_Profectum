#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar a coluna error_message na tabela recebimento_nf
"""

import sqlite3
import os

def migrate_database():
    """Adiciona a coluna error_message se não existir"""
    db_path = os.path.join('instance', 'rpa_logs.db')
    
    if not os.path.exists(db_path):
        print("[ERRO] Banco de dados nao encontrado. Execute init_database.py primeiro.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='recebimento_nf'
        """)
        
        if not cursor.fetchone():
            print("[INFO] Tabela recebimento_nf nao existe ainda")
            conn.close()
            return True
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(recebimento_nf)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'error_message' in columns:
            print("[OK] Coluna error_message ja existe")
            conn.close()
            return True
        
        # Adicionar a coluna
        print("[EXECUTANDO] Adicionando coluna error_message...")
        cursor.execute("""
            ALTER TABLE recebimento_nf 
            ADD COLUMN error_message TEXT
        """)
        
        conn.commit()
        conn.close()
        
        print("[SUCESSO] Coluna error_message adicionada com sucesso!")
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro na migracao: {str(e)}")
        return False

if __name__ == '__main__':
    print("[INICIO] Executando migracao do banco de dados...")
    if migrate_database():
        print("[CONCLUIDO] Migracao concluida!")
    else:
        print("[FALHA] Migracao falhou!")

