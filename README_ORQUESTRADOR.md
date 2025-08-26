# 🤖 RPA Profectum - Orquestrador Web

Uma interface web moderna e intuitiva para gerenciar, executar e monitorar suas automações RPA do projeto Profectum.

## ✨ Características

- **📊 Dashboard Interativo**: Visualize estatísticas e métricas em tempo real
- **🎮 Execução de Bots**: Execute automações com um clique
- **📋 Logs Detalhados**: Monitore execuções com logs em tempo real
- **🗃️ Persistência**: Todos os dados salvos em SQLite
- **🔄 Auto-refresh**: Atualizações automáticas do status
- **📱 Design Responsivo**: Interface moderna com Bootstrap
- **⚡ Tempo Real**: Monitoramento live das execuções
- **🔐 Autenticação Segura**: Sistema completo de login e gestão de usuários
- **👥 Controle de Acesso**: Perfis de administrador e usuário comum
- **🔑 Reset de Senhas**: Sistema integrado de recuperação de senhas

## 🚀 Instalação Rápida

### 1. Instalar Dependências

```bash
pip install -r requirements_web.txt
```

### 2. Configurar Credenciais

Edite o arquivo `entrada-nf/.env` (será criado automaticamente):

```env
# Configurações do Sistema SIC
SIC_USUARIO=seu_usuario_sic
SIC_SENHA=sua_senha_sic

# Configurações do Sistema RM
RM_USUARIO=seu_usuario_rm
RM_SENHA=sua_senha_rm
```

### 3. Iniciar Orquestrador

```bash
python start_rpa_orchestrator.py
```

### 4. Fazer Login

Acesse: **http://localhost:5000**

**Credenciais padrão:**
- Usuário: `profectum`
- Senha: `123456`

## 🎯 Funcionalidades

### Dashboard Principal
- **Estatísticas Gerais**: Total de execuções, sucessos, falhas
- **Gráficos**: Execuções por bot, tendências temporais
- **Execuções Recentes**: Lista das últimas automações
- **Execução Rápida**: Botões para iniciar bots rapidamente

### Gerenciamento de Bots
- **Visão Geral**: Cards com informações de cada bot
- **Execução Individual**: Controle granular de cada automação
- **Monitoramento**: Status em tempo real das execuções
- **Histórico**: Acesso ao histórico de cada bot

### Sistema de Logs
- **Logs Estruturados**: Organização por nível (INFO, WARNING, ERROR)
- **Filtros Avançados**: Por execução, data, nível, texto
- **Tempo Real**: Atualização automática durante execuções
- **Exportação**: Download de logs em diferentes formatos
- **Busca**: Pesquisa em tempo real nos logs

### Detalhes de Execução
- **Timeline**: Visualização cronológica dos eventos
- **Progresso**: Barra de progresso estimado
- **Controles**: Parar execução, visualizar logs, exportar
- **Estatísticas**: Métricas detalhadas da execução

### Sistema de Autenticação
- **Login Seguro**: Autenticação com hash de senhas
- **Sessões**: Controle de sessões com "lembrar-me"
- **Perfis de Usuário**: Administrador e usuário comum
- **Reset de Senhas**: Sistema de recuperação via token
- **Gerenciamento**: Interface para ativar/desativar usuários
- **Auditoria**: Controle de último acesso e criação

## 🔧 Bots Disponíveis

| Bot | Descrição | Duração Estimada |
|-----|-----------|------------------|
| **SIC - Processo Completo** | Login + Módulo Contábil/Fiscal | ~5 min |
| **SIC - Apenas Login** | Autenticação no sistema SIC | ~1 min |
| **RM - Login** | Autenticação no TOTVS RM | ~1 min |
| **Consulta NFe** | Validação de NFe via API | ~30s |

## 📁 Estrutura do Projeto

```
RPA_Profectum/
├── app.py                      # Aplicação Flask principal
├── start_rpa_orchestrator.py   # Script de inicialização
├── requirements_web.txt        # Dependências web
├── rpa_logs.db                # Banco SQLite (gerado automaticamente)
│
├── templates/                  # Templates HTML
│   ├── base.html              # Layout base
│   ├── dashboard.html         # Dashboard principal
│   ├── bots.html              # Gerenciamento de bots
│   ├── logs.html              # Visualização de logs
│   └── execution_details.html # Detalhes de execução
│
└── entrada-nf/                # Bots RPA existentes
    ├── bot.py                 # Bot principal (integrado)
    ├── bot_logger.py          # Sistema de logging
    ├── Sic_Login.py          # Módulo SIC Login
    ├── Sic_Modulo_Contabil.py # Módulo SIC Contábil
    ├── RM_Login.py           # Módulo RM Login
    ├── Consulta_nfe.py       # Consulta NFe
    └── .env                  # Configurações
```

## 🗄️ Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

### `user`
- **id**: ID único do usuário
- **username**: Nome de usuário (único)
- **email**: E-mail do usuário (único)
- **password_hash**: Hash da senha (bcrypt)
- **full_name**: Nome completo
- **role**: Perfil (admin, user)
- **is_active**: Status ativo/inativo
- **created_at**: Data de criação
- **last_login**: Último acesso
- **reset_token**: Token para reset de senha
- **reset_token_expires**: Expiração do token

### `bot_execution`
- **id**: ID único da execução
- **bot_name**: Nome do bot executado
- **status**: running, completed, failed, stopped
- **start_time/end_time**: Timestamps de início e fim
- **duration**: Duração em segundos
- **parameters**: Parâmetros JSON da execução
- **result**: Resultado da execução
- **error_message**: Mensagem de erro (se houver)

### `bot_log`
- **id**: ID único do log
- **execution_id**: Referência à execução
- **timestamp**: Momento do log
- **level**: INFO, WARNING, ERROR, DEBUG
- **message**: Mensagem do log
- **module**: Módulo que gerou o log

## 🔌 API Endpoints

### Autenticação
- `GET /login` - Página de login
- `POST /login` - Autenticar usuário
- `GET /logout` - Fazer logout
- `GET /reset-password` - Solicitar reset de senha
- `POST /reset-password` - Processar solicitação de reset
- `GET /reset-password/<token>` - Página de nova senha
- `POST /reset-password/<token>` - Definir nova senha

### Usuários (Admin)
- `GET /users` - Gerenciar usuários
- `GET /register` - Cadastrar novo usuário
- `POST /register` - Processar cadastro
- `POST /users/<id>/toggle-status` - Ativar/desativar
- `POST /users/<id>/delete` - Excluir usuário

### Execução
- `POST /execute/<bot_id>` - Executar bot
- `GET /api/execution/<id>/status` - Status da execução
- `POST /stop/<id>` - Parar execução

### Logs
- `GET /api/logs/<execution_id>` - Logs de uma execução
- `GET /logs` - Interface de logs com filtros

### Dashboard
- `GET /` - Dashboard principal
- `GET /bots` - Gerenciamento de bots
- `GET /execution/<id>` - Detalhes de execução

## 🎨 Interface

### Design Moderno
- **Cores**: Paleta azul profissional com gradientes
- **Ícones**: Bootstrap Icons para consistência
- **Animações**: Transições suaves e feedbacks visuais
- **Responsivo**: Adaptável a diferentes tamanhos de tela

### Componentes
- **Cards Estatísticos**: Com hover effects e ícones
- **Tabelas Modernas**: Sem bordas, com hover highlighting
- **Progress Bars**: Animadas para execuções em tempo real
- **Badges de Status**: Cores contextuais para diferentes estados
- **Modais**: Para confirmações e detalhes

## ⚙️ Configurações Avançadas

### Personalizar Porta
```python
# No app.py, altere:
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Auto-refresh
- Dashboard: Atualização automática a cada 30s
- Logs: Configurável pelo usuário (padrão 5s)
- Execuções: Monitoramento contínuo em tempo real

### Logging
O sistema de logging é integrado aos bots existentes:

```python
from bot_logger import get_logger

logger = get_logger("meu_modulo")
logger.info("Processo iniciado")
logger.step("Login", "Fazendo autenticação")
logger.success("Login concluído")
logger.error("Falha na execução")
```

## 🔍 Monitoramento

### Em Tempo Real
- **Status de Execução**: Atualização automática
- **Progresso**: Barra de progresso estimado
- **Logs Live**: Novos logs aparecem automaticamente
- **Notificações**: Toasts para eventos importantes

### Métricas
- Total de execuções
- Taxa de sucesso/falha
- Tempo médio de execução
- Execuções por período

## 🚨 Troubleshooting

### Problemas Comuns

**1. Dependências em falta**
```bash
pip install -r requirements_web.txt
```

**2. Bots não executam**
- Verifique se as credenciais estão corretas no `.env`
- Confirme se os caminhos dos scripts estão corretos
- Verifique se o Python consegue acessar os módulos

**3. Banco de dados**
- O arquivo `rpa_logs.db` é criado automaticamente
- Para resetar: delete o arquivo e reinicie a aplicação

**4. Interface não carrega**
- Verifique se a porta 5000 está disponível
- Confirme se todos os templates estão presentes

## 🔒 Segurança

- **Credenciais**: Armazenadas em variáveis de ambiente
- **Validação**: Inputs validados no frontend e backend
- **Logs**: Não expõem informações sensíveis
- **Isolamento**: Execuções em processos separados

## 🎯 Próximos Passos

- [ ] Agendamento de execuções (cron-like)
- [ ] Notificações por email/Slack
- [ ] Métricas avançadas e dashboards
- [ ] API REST completa
- [ ] Autenticação e múltiplos usuários
- [ ] Integração com CI/CD
- [ ] Backup automático do banco

## 📞 Suporte

Este orquestrador foi desenvolvido para demonstrar a integração de automações RPA com interface web moderna. Para suporte técnico ou melhorias, entre em contato com a equipe de desenvolvimento.

---

**Desenvolvido com ❤️ para automações RPA mais eficientes** 