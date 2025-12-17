# ⏰ Configurar Verificador no Agendador de Tarefas do Windows

## 🎯 Objetivo

Configurar o `verificador_romaneios.py` para rodar automaticamente a cada 5 minutos usando o Agendador de Tarefas do Windows.

---

## 📋 Passo a Passo

### 1️⃣ Abrir o Agendador de Tarefas

1. Pressione `Win + R`
2. Digite: `taskschd.msc`
3. Pressione Enter

### 2️⃣ Criar Nova Tarefa

1. No painel direito, clique em **"Criar Tarefa..."** (não "Criar Tarefa Básica")
2. Na aba **"Geral"**:
   - Nome: `Verificador de Romaneios - RPA Profectum`
   - Descrição: `Verifica romaneios a cada 5 minutos e atualiza status`
   - ✅ Marque: **"Executar com privilégios mais altos"** (se necessário)
   - Em "Configurar para": Selecione `Windows 10`

### 3️⃣ Configurar Gatilho (Trigger)

1. Vá na aba **"Gatilhos"**
2. Clique em **"Novo..."**
3. Configure:
   - **Iniciar a tarefa:** `Dentro de um agendamento`
   - **Configurações:**
     - ✅ Diariamente
     - Iniciar em: `[data de hoje]` às `00:00:00`
   - **Configurações avançadas:**
     - ✅ Marque: **"Repetir a tarefa a cada:"** `5 minutos`
     - Durante: `Indefinidamente`
     - ✅ Marque: **"Habilitado"**
4. Clique em **OK**

### 4️⃣ Configurar Ação

1. Vá na aba **"Ações"**
2. Clique em **"Novo..."**
3. Configure:
   - **Ação:** `Iniciar um programa`
   - **Programa/script:** 
     ```
     C:\Users\Marcos\Desktop\RPA_Profectum\venv\Scripts\python.exe
     ```
   - **Adicionar argumentos (opcional):**
     ```
     verificador_romaneios.py --once
     ```
   - **Iniciar em (opcional):**
     ```
     C:\Users\Marcos\Desktop\RPA_Profectum
     ```
4. Clique em **OK**

### 5️⃣ Configurar Condições

1. Vá na aba **"Condições"**
2. **Desmarque:**
   - ❌ "Iniciar a tarefa apenas se o computador estiver conectado à energia CA"
   - ❌ "Parar se o computador passar a usar energia de bateria"
3. ✅ Pode marcar: "Iniciar somente se a seguinte conexão de rede estiver disponível"
   - Selecione: `Qualquer conexão`

### 6️⃣ Configurar Configurações

1. Vá na aba **"Configurações"**
2. Configure:
   - ✅ "Permitir que a tarefa seja executada sob demanda"
   - ✅ "Executar a tarefa assim que possível após uma inicialização agendada ter sido perdida"
   - ❌ "Se a tarefa falhar, reiniciar a cada:" (desmarque, pois o agendador já vai tentar novamente em 5min)
   - **Se a tarefa já estiver em execução:**
     - Selecione: `Não iniciar uma nova instância`
3. Clique em **OK**

### 7️⃣ Salvar e Testar

1. Digite sua senha do Windows se solicitado
2. Encontre a tarefa na lista
3. Clique com botão direito → **"Executar"**
4. Verifique se funcionou!

---

## 🔧 Opção Alternativa: Usar Script BAT

Se preferir, use o arquivo `executar_verificador.bat` criado:

### No Agendador, na aba "Ações":
- **Programa/script:** 
  ```
  C:\Users\Marcos\Desktop\RPA_Profectum\executar_verificador.bat
  ```
- **Deixe os outros campos em branco**

---

## ✅ Verificar se Está Funcionando

### 1. Pelo Agendador de Tarefas:
- Abra o agendador
- Clique na tarefa
- Veja a aba **"Histórico"** (ative se estiver desabilitado)
- Última execução deve mostrar "Êxito"

### 2. Pelos Logs do Sistema:
- Os logs aparecem no banco de dados (`romaneio_log`)
- Acesse `/romaneios/<id>` no painel web e veja a timeline

### 3. Forçar Execução Manual:
- No agendador, clique com direito na tarefa
- Clique em **"Executar"**

---

## 🐛 Solução de Problemas

### Erro: "O sistema não pode encontrar o arquivo especificado"
- ✅ Verifique o caminho do Python: `C:\Users\Marcos\Desktop\RPA_Profectum\venv\Scripts\python.exe`
- ✅ Verifique se o venv existe

### Erro: "ModuleNotFoundError"
- ✅ Certifique-se de usar o Python do venv, não o global
- ✅ Reinstale dependências: `pip install -r requirements_web.txt`

### Tarefa não executa:
- ✅ Verifique as condições (energia, rede)
- ✅ Ative o histórico da tarefa
- ✅ Execute manualmente primeiro

### APIs não estão sendo chamadas:
- ✅ Verifique o `.env`: `MODO_TESTE=False` (para produção)
- ✅ Verifique `VERIFICADOR_ATIVO=True`

---

## 📊 Monitoramento

### Ver Logs em Tempo Real:
```bash
# Executar manualmente para ver logs
cd C:\Users\Marcos\Desktop\RPA_Profectum
venv\Scripts\activate
python verificador_romaneios.py --once
```

### Ver Histórico no Painel:
- Acesse: http://localhost:5000/romaneios
- Clique em um romaneio
- Veja a timeline de logs

---

## 💡 Dicas

### Múltiplas Estratégias:

**Estratégia 1: Agendador + Flask desligado**
- Use o Agendador de Tarefas (a cada 5min)
- Não precisa manter o Flask rodando

**Estratégia 2: Flask com APScheduler (Recomendado)**
- Rode apenas: `python app.py`
- O verificador roda automaticamente integrado
- Não precisa do Agendador de Tarefas

**Estratégia 3: Script em Loop**
- Rode: `python verificador_romaneios.py --loop`
- Deixe rodando em terminal/serviço
- Não precisa do Agendador de Tarefas

### Nossa Recomendação:
- **Desenvolvimento:** Usar Flask com APScheduler (`python app.py`)
- **Produção:** Usar Agendador de Tarefas + Flask separados

---

## 🎯 Checklist Final

Antes de colocar em produção:

- [ ] Arquivo `.env` configurado com `MODO_TESTE=False`
- [ ] Testado execução manual: `python verificador_romaneios.py --once`
- [ ] Tarefa criada no Agendador de Tarefas
- [ ] Testado execução via agendador (botão direito → Executar)
- [ ] Verificado logs no painel web
- [ ] Confirmado que APIs estão sendo chamadas
- [ ] Testado botão "Verificar Agora" no painel

---

## 🔗 Links Úteis

- **Painel Web:** http://localhost:5000/romaneios
- **Documentação Completa:** README_ROMANEIOS.md
- **Início Rápido:** INICIO_RAPIDO.md

---

**Configuração completa! O verificador vai rodar automaticamente a cada 5 minutos.** 🚀

