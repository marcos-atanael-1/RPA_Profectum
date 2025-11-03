# 📦 Como Usar o Sistema de Recebimento de NF

## 🎯 Visão Geral

O sistema de Recebimento de NF permite cadastrar notas fiscais pendentes e processá-las automaticamente no sistema SIC usando RPA.

---

## 🔄 Fluxo Completo

```
1. Usuário cadastra NF na interface web
   ↓
2. NF fica com status "pendente" no banco
   ↓
3. Bot "SIC - Inserir NFs Pendentes" é executado
   ↓
4. Bot busca todas NFs pendentes
   ↓
5. Para cada NF:
   - Insere no sistema SIC
   - Atualiza status para "processado" ou "erro"
   - Registra logs detalhados
```

---

## 📝 Passo a Passo

### 1️⃣ Acessar a Página de Recebimento

1. Faça login no sistema RPA Profectum
2. No menu lateral, clique em **"📦 Recebimento NF"**
3. Você verá a lista de todas as NFs cadastradas

### 2️⃣ Cadastrar Uma Nova NF

1. Clique no botão **"➕ Adicionar Recebimento"**
2. Preencha os campos:
   - **Pedido de Compra**: Número do pedido (ex: 12345)
   - **Nota Fiscal**: Número da nota fiscal (ex: 98765)
   - **Chave de Acesso**: Chave NFe com 44 caracteres
3. Clique em **"Adicionar"**
4. A NF será criada com status **"pendente"**

### 3️⃣ Executar o Bot para Processar NFs

1. No menu lateral, clique em **"🤖 Bots"**
2. Localize o bot **"SIC - Inserir NFs Pendentes"**
3. Clique em **"▶️ Executar"**
4. O bot irá:
   - Buscar todas as NFs com status "pendente"
   - Fazer login no sistema SIC (se necessário)
   - Inserir cada NF no sistema
   - Atualizar o status de cada NF

### 4️⃣ Acompanhar a Execução

**Em Tempo Real:**
1. Vá para **"📊 Dashboard"**
2. Veja as execuções em andamento
3. Acompanhe o progresso

**Após a Execução:**
1. Vá para **"📋 Logs"**
2. Busque pela execução específica
3. Veja os logs detalhados de cada etapa

### 5️⃣ Verificar Resultados

1. Volte para **"📦 Recebimento NF"**
2. As NFs processadas terão status:
   - ✅ **"processado"** - Inserida com sucesso
   - ❌ **"erro"** - Falha na inserção (veja mensagem de erro)
3. Use os filtros para encontrar NFs específicas

---

## 🔍 Filtros Disponíveis

Na página de Recebimento NF, você pode filtrar por:

- **Pedido de Compra**: Digite parte ou todo o número
- **Nota Fiscal**: Digite parte ou todo o número
- **Status**: 
  - Todos
  - Pendente
  - Processado
  - Erro

---

## 📊 Status das NFs

| Status | Descrição | Ação |
|--------|-----------|------|
| 🟡 **pendente** | Aguardando processamento | Execute o bot |
| ✅ **processado** | Inserida com sucesso no SIC | Nenhuma ação necessária |
| ❌ **erro** | Falha ao inserir | Verifique a mensagem de erro e tente novamente |

---

## 🔄 Reprocessar NFs com Erro

Se uma NF teve erro e você deseja reprocessá-la:

1. **Opção A - Editar Status Manualmente:**
   - Acesse o banco de dados (SQLite)
   - Altere o status de "erro" para "pendente"
   - Execute o bot novamente

2. **Opção B - Criar Nova NF:**
   - Cadastre a NF novamente
   - Certifique-se de que os dados estão corretos
   - Execute o bot

---

## 📋 Campos Obrigatórios

| Campo | Formato | Exemplo | Observações |
|-------|---------|---------|-------------|
| **Pedido de Compra** | Texto/Números | "12345" | Sem restrições |
| **Nota Fiscal** | Texto/Números | "98765" | Sem restrições |
| **Chave de Acesso** | 44 caracteres | "35210..." | Deve ter exatamente 44 caracteres |

---

## 🤖 Detalhes do Bot "SIC - Inserir NFs Pendentes"

**Nome do Script:** `entrada-nf/Sic_Inserir_NF.py`

**O que faz:**
1. Conecta ao banco de dados SQLite
2. Busca todas as NFs com `status = 'pendente'`
3. Para cada NF:
   - Clica no botão "+" para adicionar NF
   - Preenche o Pedido de Compra
   - Preenche a Chave de Acesso
   - Preenche a Nota Fiscal
   - Clica em "Adicionar NF"
   - Atualiza o status no banco

**Tempo Estimado:** 180 segundos (3 minutos)

**Logs Gerados:**
- 📋 Quantidade de NFs encontradas
- 📝 Detalhes de cada preenchimento
- ✅ NFs processadas com sucesso
- ❌ NFs com erro e motivo

---

## 🛠️ Integração com o Bot Principal

Se você quiser incluir o processamento de NFs no fluxo completo do `bot.py`:

```python
# No arquivo entrada-nf/bot.py

# Etapa: Inserir NFs pendentes
logger.step("Inserir NFs", "Processando notas fiscais pendentes")
Sic_Inserir_NF()
logger.success("NFs processadas")
```

---

## 📊 Relatórios e Estatísticas

Ao final de cada execução, o bot exibe um relatório:

```
====================================================
📊 Processamento concluído!
   ✅ Processadas com sucesso: 5
   ❌ Com erro: 1
   📋 Total: 6
====================================================
```

Esses dados também ficam salvos nos logs da execução.

---

## ⚠️ Avisos Importantes

1. **Pré-requisitos:**
   - O sistema SIC deve estar acessível
   - O login no SIC deve ter sido feito
   - As imagens de referência devem estar corretas:
     - `Adicionar_NF.png`
     - `Sic_Chave_NF_Label.png`
     - `Sic_Botao_Adicionar_NF.png`

2. **Chave de Acesso:**
   - Deve ter **exatamente 44 caracteres**
   - Valide antes de cadastrar

3. **Duplicidade:**
   - O sistema impede cadastrar NFs com a mesma chave de acesso
   - Se tentar cadastrar duplicada, receberá uma mensagem de erro

---

## 🔧 Tabela do Banco de Dados

**Nome:** `recebimento_nf`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER | ID único (auto-incremento) |
| pedido_compra | VARCHAR(100) | Número do pedido |
| nota_fiscal | VARCHAR(100) | Número da NF |
| chave_acesso | VARCHAR(44) | Chave NFe (44 chars) |
| created_at | DATETIME | Data/hora de criação |
| created_by | INTEGER | ID do usuário criador |
| status | VARCHAR(20) | pendente/processado/erro |
| error_message | TEXT | Mensagem de erro (se houver) |

---

## 📞 Suporte

Em caso de problemas:

1. Verifique os **logs** da execução
2. Confirme que as **imagens de referência** estão corretas
3. Teste o **login manual** no SIC
4. Verifique se a **chave de acesso** é válida

---

## ✅ Checklist Rápido

- [ ] NFs cadastradas com status "pendente"
- [ ] Chaves de acesso com 44 caracteres
- [ ] Sistema SIC acessível
- [ ] Bot "SIC - Inserir NFs Pendentes" executado
- [ ] Logs verificados
- [ ] Status das NFs atualizado
- [ ] NFs com erro revisadas

---

## 🎯 Próximos Passos

Após dominar o sistema de Recebimento de NF, você pode:

1. **Automatizar o processo:** Configure execuções agendadas
2. **Integrar com APIs:** Buscar NFs automaticamente de outros sistemas
3. **Criar relatórios:** Exportar dados de NFs processadas
4. **Notificações:** Receber alertas quando NFs forem processadas

---

**Sistema RPA Profectum** - Automatizando seus processos! 🤖✨

