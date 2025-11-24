# 🧪 Guia de Configuração e Testes - Carteira Digital API

---

## 📋 PARTE 1: Configuração Inicial do Ambiente

### 🔧 Passo 1: Iniciar o MySQL

**Escolha UMA das opções:**

#### **Opção A: XAMPP** (mais comum)
1. Abra o **XAMPP Control Panel**
2. Clique em **Start** ao lado de **MySQL**
3. Aguarde até aparecer "Running" em verde

#### **Opção B: Serviços do Windows**
1. Pressione `Win + R`, digite: `services.msc`
2. Procure "MySQL" ou "MySQL80"
3. Clique com botão direito → **Iniciar**

#### **Opção C: PowerShell (Administrador)**
```powershell
Start-Service MySQL80
```

**✅ Verificar se MySQL está rodando:**
```powershell
Test-NetConnection -ComputerName localhost -Port 3306
```
**Resultado esperado:** `TcpTestSucceeded : True`

---

### 🗄️ Passo 2: Criar o Banco de Dados

#### **Opção A: MySQL Workbench** (Recomendado)
1. Abra o **MySQL Workbench**
2. Conecte ao servidor (usuário: `root`)
3. **File** → **Open SQL Script**
4. Abra: `sql/DDL_Carteira_Digital.sql`
5. Clique no ícone ⚡ para executar
6. Aguarde a conclusão

#### **Opção B: Linha de Comando**
```bash
mysql -u root -p < sql/DDL_Carteira_Digital.sql
```
Digite a senha do root quando solicitado.

**✅ Verificar criação do banco:**
```bash
mysql -u root -p -e "SHOW DATABASES LIKE 'wallet%';"
```
**Resultado esperado:** `wallet_homolog`

**✅ Verificar tabelas (deve ter 6):**
```bash
mysql -u root -p -e "USE wallet_homolog; SHOW TABLES;"
```
**Tabelas esperadas:**
- carteira
- conversao
- deposito_saque
- moeda
- saldo_carteira
- transferencia

**✅ Verificar moedas (deve ter 5):**
```bash
mysql -u root -p -e "USE wallet_homolog; SELECT codigo, nome FROM moeda;"
```
**Moedas esperadas:** BRL, BTC, ETH, SOL, USD

---

### 🚀 Passo 3: Iniciar a API

```bash
cd C:\Users\guilh\Desktop\ProjetoBD\WalletDb_v2
python -m uvicorn api.main:app --reload
```

**✅ Resultado esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**🌐 Acessar documentação:** http://127.0.0.1:8000/docs

---

## 📋 PARTE 2: Executando os Testes

### ✅ Pré-requisitos
- [x] MySQL rodando na porta 3306
- [x] Banco `wallet_homolog` criado com 6 tabelas
- [x] API rodando em http://127.0.0.1:8000
- [x] Swagger aberto em http://127.0.0.1:8000/docs

---

### 🧪 Sequência de Testes no Swagger

Acesse: **http://127.0.0.1:8000/docs**

---

#### **Teste 1: Health Check**
1. Execute `GET /`
2. **Esperado:** `{"status": "ok", "message": "Carteira Digital API está funcionando!"}`

---

#### **Teste 2: Criar Carteira**
1. Execute `POST /carteiras`
2. **Copie e GUARDE:**
   - `endereco_carteira`
   - `chave_privada` (só aparece uma vez!)

---

#### **Teste 3: Ver Saldos Iniciais**
1. Execute `GET /carteiras/{endereco}/saldos`
2. Cole o endereço da carteira
3. **Esperado:** 5 moedas com saldo 0.0

---

#### **Teste 4: Fazer Depósito**
1. Execute `POST /carteiras/{endereco}/depositos`
2. Body:
```json
{
  "codigo_moeda": "BTC",
  "valor": 2.0
}
```
3. **Esperado:** tipo: "DEPOSITO", taxa: 0.0

---

#### **Teste 5: Verificar Saldo Atualizado**
1. Execute `GET /carteiras/{endereco}/saldos`
2. **Esperado:** BTC com saldo 2.0

---

#### **Teste 6: Fazer Saque (com taxa)**
1. Execute `POST /carteiras/{endereco}/saques`
2. Body:
```json
{
  "codigo_moeda": "BTC",
  "valor": 0.5,
  "chave_privada": "COLE_SUA_CHAVE_AQUI"
}
```
3. **Esperado:** tipo: "SAQUE", taxa: 0.005 (1%)

---

#### **Teste 7: Testar Segurança (chave errada)**
1. Tente saque com `"chave_privada": "chave_errada"`
2. **Esperado:** Erro 400: "Chave privada inválida"

---

#### **Teste 8: Fazer Mais Depósitos**
Deposite USD e BRL para ter saldo para conversões:
```json
{"codigo_moeda": "USD", "valor": 100000}
{"codigo_moeda": "BRL", "valor": 50000}
```

---

#### **Teste 9: Conversão entre Moedas**
1. Execute `POST /carteiras/{endereco}/conversoes`
2. Body:
```json
{
  "moeda_origem": "BTC",
  "moeda_destino": "USD",
  "valor_origem": 0.1,
  "chave_privada": "COLE_SUA_CHAVE_AQUI"
}
```
3. **Esperado:** 
   - cotacao: preço atual do BTC em USD
   - taxa: 2% do valor convertido
   - Saldo BTC diminui, saldo USD aumenta

---

#### **Teste 10: Criar Segunda Carteira**
1. Execute `POST /carteiras`
2. **Guarde** endereço e chave da Carteira 2

---

#### **Teste 11: Transferência entre Carteiras**
1. Faça depósito na Carteira 1: `{"codigo_moeda": "BTC", "valor": 1.0}`
2. Execute `POST /carteiras/{endereco_carteira1}/transferencias`
3. Body:
```json
{
  "endereco_destino": "ENDERECO_CARTEIRA_2",
  "codigo_moeda": "BTC",
  "valor": 0.3,
  "chave_privada": "CHAVE_CARTEIRA_1"
}
```
4. **Esperado:**
   - Taxa: 0.0045 (1.5%)
   - Carteira 1 perde: 0.3 + 0.0045 = 0.3045 BTC
   - Carteira 2 recebe: 0.3 BTC

---

#### **Teste 12: Listar Todas as Carteiras**
1. Execute `GET /carteiras`
2. **Esperado:** Lista com 2 carteiras

---

#### **Teste 13: Bloquear Carteira**
1. Crie uma terceira carteira
2. Execute `DELETE /carteiras/{endereco}`
3. **Esperado:** status: "BLOQUEADA"
4. Tente depositar nela → Deve retornar erro

---

## 📊 PARTE 3: Checklist de Validação

### Funcionalidades Básicas
- [ ] Health check funcionando
- [ ] Criar carteira
- [ ] Buscar carteira
- [ ] Listar carteiras
- [ ] Ver saldos

### Operações Financeiras
- [ ] Depósito sem taxa
- [ ] Saque com taxa 1%
- [ ] Conversão com taxa 2%
- [ ] Transferência com taxa 1.5%

### Segurança
- [ ] Validação de chave privada funciona
- [ ] Chave só retornada na criação
- [ ] Carteira bloqueada não permite operações

### Validações de Erro
- [ ] Saldo insuficiente bloqueia
- [ ] Chave inválida bloqueia
- [ ] Carteira inexistente retorna 404

---

## 🆘 Solução de Problemas

### ❌ "Can't connect to MySQL server"
**Causa:** MySQL não está rodando  
**Solução:** Inicie o MySQL (veja Passo 1)

### ❌ "Unknown database 'wallet_homolog'"
**Causa:** Banco não foi criado  
**Solução:**
```bash
mysql -u root -p < sql/DDL_Carteira_Digital.sql
```

### ❌ "Access denied for user"
**Causa:** Usuário não foi criado  
**Solução:**
```sql
mysql -u root -p
CREATE USER 'wallet_api_homolog'@'%' IDENTIFIED BY 'api123';
GRANT SELECT, INSERT, UPDATE, DELETE ON wallet_homolog.* TO 'wallet_api_homolog'@'%';
FLUSH PRIVILEGES;
```

### ❌ Erro 500 ao criar carteira
**Causa:** Problema nas tabelas  
**Solução:** Re-execute o DDL completo

---

## 🔧 Comandos Úteis

**Parar API:** `Ctrl+C` no terminal

**Reiniciar API:**
```bash
python -m uvicorn api.main:app --reload
```

**Limpar banco (recomeçar):**
```sql
DROP DATABASE wallet_homolog;
-- Depois execute o DDL novamente
```

---

## ✅ Resultado Final Esperado

✅ 2+ carteiras criadas  
✅ Depósitos, saques, conversões e transferências realizados  
✅ Saldos calculados corretamente  
✅ Validações de segurança funcionando  
✅ API sem erros  

---

**Sucesso nos testes! 🚀**
