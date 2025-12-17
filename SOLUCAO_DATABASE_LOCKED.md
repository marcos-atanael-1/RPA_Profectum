# 🔒 Solução para "Database is Locked"

## 🎯 Problema

O erro `sqlite3.OperationalError: database is locked` ocorre quando múltiplos processos tentam acessar o banco SQLite ao mesmo tempo.

## ✅ Solução Aplicada

### 1. **Configurações Adicionadas ao Flask** (`app.py`)

```python
# Configurações do SQLAlchemy para SQLite
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'timeout': 30,              # 30 segundos de timeout
        'check_same_thread': False  # Permite múltiplas threads
    }
}

# WAL Mode habilitado automaticamente
@app.before_request
def setup_database():
    if not hasattr(app, 'db_configured'):
        try:
            with db.engine.connect() as conn:
                conn.execute(text('PRAGMA journal_mode=WAL'))     # Write-Ahead Logging
                conn.execute(text('PRAGMA busy_timeout=30000'))   # 30s timeout
                conn.commit()
            app.db_configured = True
        except:
            pass
```

### 2. **Banco de Dados Otimizado**

O script `fix_db_lock.py` configurou:
- ✅ **WAL Mode** (Write-Ahead Logging) - Permite leituras simultâneas
- ✅ **Busy Timeout** de 30 segundos - Aguarda antes de dar erro
- ✅ **Banco otimizado** com VACUUM
- ✅ **Integridade verificada**

## 📋 Como Evitar o Problema

### ❌ **NÃO FAÇA:**

1. **NÃO rode múltiplas instâncias do Flask manualmente**
   ```powershell
   # ERRADO: Ter 2 ou mais terminais rodando isso
   python app.py
   python app.py  # ❌ Segunda instância!
   ```

2. **NÃO rode `verificador_romaneios.py` manualmente**
   ```powershell
   # ERRADO: Rodar manualmente enquanto Flask está ativo
   python verificador_romaneios.py --loop  # ❌
   ```

3. **NÃO use ferramentas que travam o banco**
   - DB Browser for SQLite aberto em modo edição
   - Scripts SQL longos sem commit

### ✅ **FAÇA:**

1. **Uma única instância do Flask**
   ```powershell
   # CORRETO: Apenas uma vez
   python app.py
   ```

2. **Use o Agendador de Tarefas para o verificador**
   - O verificador deve rodar via Windows Task Scheduler
   - Executar `verificador_romaneios.py --once` (não `--loop`)
   - Intervalo recomendado: 5 minutos

3. **Se precisar resetar tudo**
   ```powershell
   # Parar todos os processos Python do projeto
   Get-Process python | Where-Object {$_.Path -like "*RPA_Profectum*"} | Stop-Process -Force
   
   # Configurar o banco
   python fix_db_lock.py
   
   # Reiniciar o Flask
   python app.py
   ```

## 🔧 Comandos Úteis

### **Ver processos Python rodando:**
```powershell
Get-Process python | Select-Object Id, ProcessName, Path
```

### **Parar todos os processos do projeto:**
```powershell
Get-Process python | Where-Object {$_.Path -like "*RPA_Profectum*"} | Stop-Process -Force
```

### **Reconfigurar banco de dados:**
```powershell
python fix_db_lock.py
```

### **Verificar status do banco:**
```powershell
# Via Python
python -c "import sqlite3; conn = sqlite3.connect('instance/rpa_logs.db'); c = conn.cursor(); c.execute('PRAGMA journal_mode'); print(c.fetchone()); conn.close()"
```

## 🚀 Workflow Recomendado

### **Desenvolvimento:**
```powershell
# 1. Iniciar apenas o Flask
python app.py

# 2. Testar criação de usuários, romaneios, etc.

# 3. Para testar o verificador (quando necessário)
#    - Pare o Flask (Ctrl+C)
#    - Execute: python verificador_romaneios.py --once
#    - Reinicie o Flask
```

### **Produção:**
```powershell
# 1. Flask rodando como serviço
python app.py

# 2. Agendador de Tarefas executando a cada 5 minutos:
#    Comando: python verificador_romaneios.py --once
#    Diretório: C:\Users\Marcos\Desktop\RPA_Profectum
```

## 🎯 Resumo

| Aspecto | Configuração |
|---------|-------------|
| **Journal Mode** | WAL (Write-Ahead Logging) |
| **Timeout** | 30 segundos |
| **Instâncias Flask** | Apenas 1 |
| **Verificador** | Via Task Scheduler (--once) |
| **Intervalo Verificação** | 5 minutos |

## ✅ Melhorias Implementadas

1. ✅ Timeout aumentado para 30 segundos
2. ✅ WAL mode habilitado (permite leituras simultâneas)
3. ✅ Pool de conexões otimizado
4. ✅ Tratamento de erro melhorado (mensagem mais clara)
5. ✅ Script `fix_db_lock.py` para resolver problemas
6. ✅ Documentação completa

---

**Agora o sistema está preparado para lidar com múltiplos acessos sem travar! 🎉**

