# 📦 Sistema de Gerenciamento de Romaneios - RPA Profectum

## 🎯 Visão Geral

Sistema completo para gerenciamento de romaneios via API, substituindo o processo RPA anterior. O sistema permite:

- ✅ Criar romaneios via painel web
- ✅ Acompanhar status em tempo real
- ✅ Verificação automática de quantidades
- ✅ Controle de tentativas de contagem
- ✅ Integração com API externa
- ✅ Modo teste para desenvolvimento

---

## 📋 Status de Romaneios

| Status | Código | Descrição |
|--------|--------|-----------|
| 🟡 **Pendente** | P | Aguardando contagem ou com divergências |
| 🟢 **Aberto** | A | Todas as quantidades conferidas e batendo |
| 🔵 **Recebido** | R | Romaneio recebido |
| ⚫ **Finalizado** | F | Processo finalizado |

---

## 🚀 Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements_web.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (ou copie o `.env.example`):

```bash
# API Romaneios
API_BASE_URL=http://172.16.17:3600
API_SYSTEM_ID=sys_1f02a9e8b5f24d73b8e74d8fae931c64_prod

# Modo de Operação
MODO_TESTE=True  # True = não chama APIs (teste), False = produção

# Verificador Automático
INTERVALO_VERIFICACAO_MINUTOS=5
MAX_TENTATIVAS_CONTAGEM=3
VERIFICADOR_ATIVO=True
VERIFICADOR_LOG_DETALHADO=True
```

⚠️ **IMPORTANTE**: Configure `MODO_TESTE=False` apenas quando estiver pronto para produção!

### 3. Migrar Banco de Dados

```bash
python migrate_romaneios.py
```

Este script criará as novas tabelas sem afetar os dados existentes (user, bot_execution, etc).

### 4. Iniciar o Sistema

```bash
python app.py
```

O sistema estará disponível em: `http://localhost:5000`

**Credenciais padrão:**
- Usuário: `profectum`
- Senha: `123456`

---

## 📱 Como Usar

### 1. Criar Novo Romaneio

1. Acesse **Romaneios** no menu
2. Clique em **Novo Romaneio**
3. Preencha:
   - Pedido de Compra (obrigatório)
   - Nota Fiscal (obrigatória)
   - Chave de Acesso NFe - 44 dígitos (obrigatória)
   - Observações (opcional)
4. Configure as opções da API se necessário
5. Clique em **Criar Romaneio**

✅ O sistema irá:
- Salvar o romaneio no banco com status **Pendente**
- Se `MODO_TESTE=False`: Chamar a API para inserir o romaneio
- Criar um log de criação

### 2. Acompanhar Romaneios

Na página de **listagem**:
- 📊 Veja estatísticas por status (cards no topo)
- 🔍 Use os filtros para buscar romaneios específicos
- 👁️ Clique no ícone de "olho" para ver detalhes
- 🔄 Clique no ícone de "sync" para forçar verificação
- 🗑️ Exclua romaneios pendentes sem tentativas

### 3. Ver Detalhes de um Romaneio

Na página de **detalhes**:
- 📋 Informações completas do romaneio
- 📦 Lista de itens com quantidades
- ⚠️ Destaque visual para divergências
- 📜 Timeline completa de ações
- 🔄 Botão para verificar manualmente
- ⚙️ Admins podem atualizar status manualmente

---

## 🤖 Verificação Automática

### Opção 1: Integrado ao Flask (Recomendado)

O verificador roda automaticamente quando o app.py está ativo:

```bash
python app.py
```

✅ Vantagens:
- Não precisa gerenciar processo separado
- Roda junto com o painel web
- Logs visíveis no console do Flask

### Opção 2: Script Standalone

Execute o verificador como processo separado:

**Uma única vez:**
```bash
python verificador_romaneios.py --once
```

**Em loop contínuo:**
```bash
python verificador_romaneios.py --loop
```

✅ Vantagens:
- Pode rodar independentemente do Flask
- Ideal para produção (como serviço Windows/Linux)
- Logs dedicados

### Como Funciona a Verificação?

A cada `INTERVALO_VERIFICACAO_MINUTOS` (padrão: 5 minutos):

1. **Busca** todos os romaneios não finalizados (status != F)
2. Para cada romaneio:
   - Verifica se pode ser verificado (tentativas < max)
   - Faz GET na API para buscar dados atualizados
   - Compara `QUANTIDADE_CONTADA` vs `QUANTIDADE_NF`
   - **Se todas batem**: Atualiza para "Aberto" (A)
   - **Se há divergências**: Incrementa tentativas
   - **Se atingiu max tentativas**: Registra e para de verificar
3. **Salva** tudo no banco e cria logs

---

## 🧪 Modo Teste vs Produção

### Modo Teste (`MODO_TESTE=True`)

✅ **Seguro para desenvolvimento**
- NÃO chama as APIs externas reais
- Simula respostas da API
- Salva tudo no banco local
- Mostra badge "MODO TESTE" na interface

### Modo Produção (`MODO_TESTE=False`)

⚠️ **Apenas quando estiver pronto!**
- Chama as APIs externas reais
- POST `/api/romaneio/inserir` ao criar romaneio
- GET `/api/romaneio/{pedido}` para verificar
- PUT `/api/romaneio/atualizar/{idro}` para atualizar status

---

## 📊 Estrutura do Banco de Dados

### Novas Tabelas Criadas

#### `romaneio`
- Informações principais do romaneio
- Status, tentativas, timestamps
- Relacionamento com User (criador)

#### `romaneio_item`
- Itens do romaneio
- Quantidades (NF vs Contada)
- Relacionamento com romaneio

#### `romaneio_log`
- Histórico completo de ações
- Mudanças de status
- Detalhes de divergências

### Tabelas Mantidas (Não Afetadas)
- ✅ `user` - Usuários e login
- ✅ `bot_execution` - Execuções de bots
- ✅ `bot_log` - Logs de bots
- ✅ `system_settings` - Configurações do sistema
- ✅ `recebimento_nf` - Recebimentos de NF

---

## 🔧 Comandos Úteis

### Verificar status do banco
```bash
python -c "from app import app, db; from models.romaneio import Romaneio; app.app_context().__enter__(); print(f'Total romaneios: {Romaneio.query.count()}')"
```

### Executar verificação manual
```bash
python verificador_romaneios.py --once
```

### Reinstalar dependências
```bash
pip install -r requirements_web.txt --upgrade
```

---

## 🎨 Endpoints da API

### Romaneios

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/romaneios` | Página de listagem |
| GET | `/romaneios/<id>` | Detalhes do romaneio |
| POST | `/api/romaneios` | Criar novo romaneio |
| GET | `/api/romaneios/<id>` | Buscar dados (JSON) |
| DELETE | `/api/romaneios/<id>` | Excluir romaneio |
| POST | `/api/romaneios/<id>/verificar` | Forçar verificação |
| PUT | `/api/romaneios/<id>/status` | Atualizar status (admin) |
| GET | `/api/romaneios/<id>/logs` | Buscar histórico |

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'config'"
```bash
pip install python-dotenv
```
Certifique-se de que o arquivo `config.py` existe na raiz.

### Erro: "Table 'romaneio' doesn't exist"
```bash
python migrate_romaneios.py
```

### Verificador não está rodando
1. Verifique `VERIFICADOR_ATIVO=True` no `.env`
2. Verifique se o Flask está rodando
3. Ou execute manualmente: `python verificador_romaneios.py --loop`

### APIs não estão sendo chamadas
1. Verifique `MODO_TESTE=False` no `.env`
2. Verifique conectividade com a API (ping/curl)
3. Verifique o `API_SYSTEM_ID` está correto

---

## 📂 Estrutura de Arquivos

```
RPA_Profectum/
├── app.py                      # Aplicação Flask principal
├── config.py                   # Configurações (lê .env)
├── .env                        # Variáveis de ambiente (criar)
├── .env.example               # Template do .env
├── migrate_romaneios.py        # Script de migração do banco
├── verificador_romaneios.py    # Verificador standalone
│
├── models/
│   ├── __init__.py
│   └── romaneio.py            # Modelos Romaneio, Item, Log
│
├── services/
│   ├── __init__.py
│   ├── api_client.py          # Cliente da API externa
│   ├── romaneio_service.py    # Lógica de negócio
│   └── verificador_service.py # Lógica de verificação
│
├── templates/
│   ├── base.html              # Template base (atualizado)
│   └── romaneios/
│       ├── lista.html         # Listagem de romaneios
│       └── detalhes.html      # Detalhes do romaneio
│
├── static/
│   └── js/
│       └── romaneios.js       # JavaScript frontend
│
└── instance/
    └── rpa_logs.db            # Banco de dados SQLite
```

---

## 🎓 Conceitos Importantes

### Tentativas de Contagem

- Cada romaneio tem no máximo **3 tentativas** (configurável)
- A cada verificação, incrementa o contador
- Ao atingir o máximo, para de verificar automaticamente
- Admin pode forçar verificação ou atualizar status manualmente

### Divergências

Uma divergência ocorre quando:
- `QUANTIDADE_CONTADA` é `null` (não foi contado)
- `QUANTIDADE_CONTADA` ≠ `QUANTIDADE_NF`

### Fluxo Normal

```
Criar → [P] Pendente → Verificar → Divergências? 
                                       ↓ Não
                                    [A] Aberto → [R] Recebido → [F] Finalizado
                                       ↓ Sim
                                 [P] Pendente (tenta novamente)
                                       ↓ 3 tentativas
                                   Alerta manual
```

---

## ✅ Checklist de Produção

Antes de colocar em produção:

- [ ] Configurar `.env` com credenciais reais
- [ ] Definir `MODO_TESTE=False`
- [ ] Testar conectividade com API externa
- [ ] Executar migração: `python migrate_romaneios.py`
- [ ] Fazer backup do banco: `cp instance/rpa_logs.db instance/rpa_logs.db.backup`
- [ ] Testar criação de romaneio
- [ ] Testar verificação automática
- [ ] Configurar monitoramento/logs
- [ ] Documentar procedimentos operacionais

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Confira os logs no console
3. Verifique a tabela `romaneio_log` no banco

---

**Desenvolvido para RPA Profectum** 🚀
Versão: 2.0 - Sistema de Romaneios via API

