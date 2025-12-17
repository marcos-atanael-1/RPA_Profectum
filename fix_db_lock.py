#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para resolver problemas de database locked no SQLite
"""

import sqlite3
import os
import sys

# Caminho do banco de dados
DB_PATH = os.path.join('instance', 'rpa_logs.db')

def fix_database():
    """Configura o banco de dados para WAL mode e otimiza configurações"""
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados nao encontrado: {DB_PATH}")
        return False
    
    try:
        print("[INFO] Configurando banco de dados...")
        
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cursor = conn.cursor()
        
        # Habilitar WAL mode (Write-Ahead Logging)
        print("[INFO] Habilitando WAL mode...")
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Configurar busy timeout (30 segundos)
        print("[INFO] Configurando timeout...")
        cursor.execute("PRAGMA busy_timeout=30000;")
        
        # Otimizar banco
        print("[INFO] Otimizando banco de dados...")
        cursor.execute("VACUUM;")
        
        # Verificar integridade
        print("[INFO] Verificando integridade...")
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        
        if result[0] == 'ok':
            print("[OK] Banco de dados esta integro!")
        else:
            print(f"[AVISO] Problema encontrado: {result[0]}")
        
        # Mostrar configurações atuais
        print("\n[CONFIG] Configuracoes atuais:")
        cursor.execute("PRAGMA journal_mode;")
        print(f"   Journal mode: {cursor.fetchone()[0]}")
        
        cursor.execute("PRAGMA synchronous;")
        print(f"   Synchronous: {cursor.fetchone()[0]}")
        
        conn.commit()
        conn.close()
        
        print("\n[OK] Banco de dados configurado com sucesso!")
        print("\n[DICAS]")
        print("   1. Certifique-se de que apenas UMA instancia do Flask esta rodando")
        print("   2. Feche o script verificador_romaneios.py se estiver rodando manualmente")
        print("   3. Use o agendador de tarefas para o verificador_romaneios.py")
        print("   4. Reinicie o servidor Flask apos essas alteracoes")
        
        return True
        
    except sqlite3.Error as e:
        print(f"[ERRO] Erro ao configurar banco: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Script de Correcao - Database Locked")
    print("=" * 60)
    print()
    
    success = fix_database()
    
    print()
    print("=" * 60)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

