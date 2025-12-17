# 🚀 INÍCIO RÁPIDO - Sistema de Romaneios

## ⚡ Em 5 Minutos

### Passo 1: Instalar Dependências
```bash
pip install -r requirements_web.txt
```

### Passo 2: Criar Arquivo .env

Crie um arquivo chamado `.env` na raiz do projeto com:

```bash
# MODO TESTE (não chama APIs reais)
MODO_TESTE=True

# API (configure depois para produção)
API_BASE_URL=http://172.16.17:3600
API_SYSTEM_ID=sys_1f02a9e8b5f24d73b8e74d8fae931c64_prod

# Verificador
INTERVALO_VERIFICACAO_MINUTOS=5
MAX_TENTATIVAS_CONTAGEM=3
VERIFICADOR_ATIVO=True
```

### Passo 3: Criar Tabelas no Banco
```bash
python migrate_romaneios.py
```

### Passo 4: Iniciar o Sistema
```bash
python app.py
```

### Passo 5: Acessar o Painel

Abra o navegador em: **http://localhost:5000**

**Login:**
- Usuário: `profectum`
- Senha: `123456`

---

## 🎯 Primeiro Romaneio

1. Clique em **Romaneios** no menu
2. Clique em **Novo Romaneio**
3. Preencha:
   - Pedido: `000285847`
   - NF: `000123`
   - Chave: `35250123456789000123550010001234567890123456` (44 dígitos)
4. Clique em **Criar Romaneio**

✅ Pronto! Seu primeiro romaneio foi criado.

---

## 🔍 Verificar Romaneio

### Opção 1: Automático (a cada 5 minutos)
O sistema já está verificando automaticamente! Aguarde 5 minutos ou...

### Opção 2: Manual
1. Na lista de romaneios, clique no ícone 🔄 (sync)
2. Ou na página de detalhes, clique em **Verificar Agora**

---

## ⚙️ Passar para Produção

Quando estiver pronto para usar com a API real:

1. Edite o arquivo `.env`:
   ```bash
   MODO_TESTE=False
   ```

2. Reinicie o sistema:
   ```bash
   # Ctrl+C para parar
   python app.py
   ```

⚠️ **ATENÇÃO:** Com `MODO_TESTE=False`, o sistema vai:
- Chamar a API real em `http://172.16.17:3600`
- Fazer POST para `/api/romaneio/inserir` para inserir romaneios
- Fazer PUT para atualizar status
- Fazer GET para verificar quantidades

---

## 📊 Status dos Romaneios

| Status | Significado |
|--------|-------------|
| 🟡 Pendente | Aguardando contagem ou com divergências |
| 🟢 Aberto | Quantidades conferidas e batendo |
| 🔵 Recebido | Romaneio recebido |
| ⚫ Finalizado | Processo completo |

---

## 🔧 Comandos Úteis

### Verificar uma vez só (sem loop)
```bash
python verificador_romaneios.py --once
```

### Verificador em loop (cada 5min)
```bash
python verificador_romaneios.py --loop
```

### Ver logs do verificador
Os logs aparecem no console onde você rodou `python app.py`

---

## ❓ Problemas Comuns

### "ModuleNotFoundError"
```bash
pip install -r requirements_web.txt
```

### "Table doesn't exist"
```bash
python migrate_romaneios.py
```

### "Verificador não roda"
Verifique no `.env`:
```bash
VERIFICADOR_ATIVO=True
```

### "API não responde"
Você está em modo teste? Verifique:
```bash
MODO_TESTE=True  # não chama API
MODO_TESTE=False # chama API real
```

---

## 📚 Documentação Completa

Para mais detalhes, consulte:
- **README_ROMANEIOS.md** - Documentação completa
- **RESUMO_IMPLEMENTACAO.md** - O que foi implementado

---

## 🎉 Pronto!

Seu sistema de romaneios está funcionando!

**Próximos passos:**
1. Criar alguns romaneios de teste
2. Aguardar verificação automática
3. Conferir os detalhes e logs
4. Quando estiver confortável, ativar modo produção

**Divirta-se!** 🚀

