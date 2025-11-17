# Projeto Carteira Digital 🪙

Este projeto implementa uma **API de Carteira Digital** completa para a disciplina Projeto de Banco de Dados:

- **FastAPI**
- **MySQL**
- **SQLAlchemy (Core, sem ORM)**
- **SQL puro para DDL/DML**
- Integração com API pública da **Coinbase** para conversão de moedas

A carteira permite:

- ✅ Criar carteiras (com chave pública e chave privada)
- ✅ Ver saldos por moeda (BTC, ETH, SOL, USD, BRL)
- ✅ Fazer **depósitos** (sem taxa)
- ✅ Fazer **saques** (com taxa e validação da chave privada)
- ✅ Fazer **conversão entre moedas** (usando cotação da Coinbase + taxa)
- ✅ Fazer **transferência entre carteiras** (com taxa na origem)

---

## 1. Pré-requisitos

Antes de começar, você precisa ter instalado:

- Python 3.10+
- MySQL 8+
- git (opcional)

Verifique as versões:

```bash
python --version
mysql --version
```

---

## 2. Clonar ou baixar o projeto

```bash
git clone https://github.com/timotrob/WalletDb_v2.git
cd WalletDb_v2
```

Ou extraia o ZIP e abra o terminal dentro da pasta do projeto.

---

## 3. Criar e ativar o ambiente virtual (venv)

### Windows:
```bash
python -m venv venv
venv\Scripts\Activate
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 5. Criar o banco e usuário no MySQL

Abra o MySQL e execute o script DDL:

```bash
mysql -u root -p < sql/DDL_Carteira_Digital.sql
```

Ou dentro do MySQL:

```sql
SOURCE sql/DDL_Carteira_Digital.sql;
```

Isso irá:

- Criar o banco `wallet_homolog`
- Criar usuário restrito `wallet_api_homolog` com senha `api123`
- Criar todas as tabelas necessárias (carteira, moeda, saldo_carteira, deposito_saque, conversao, transferencia)
- Inserir as 5 moedas obrigatórias (BTC, ETH, SOL, USD, BRL)

---

## 6. Criar o arquivo `.env`

Copie o arquivo de exemplo e ajuste se necessário:

```bash
cp .env.example .env
```

Conteúdo padrão do `.env`:

```env
# Configurações de Banco de Dados
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wallet_homolog
DB_USER=wallet_api_homolog
DB_PASSWORD=api123

# Configurações de Chaves
PRIVATE_KEY_SIZE=32
PUBLIC_KEY_SIZE=32

# Taxas (valores decimais, ex: 0.01 = 1%)
TAXA_SAQUE=0.01
TAXA_CONVERSAO=0.02
TAXA_TRANSFERENCIA=0.015
```

---

## 7. Estrutura do projeto

```
WalletDb_v2/
│
├── api/
│   ├── main.py                    # Aplicação FastAPI principal
│   │
│   ├── models/
│   │   ├── carteira_models.py     # Modelos Pydantic para carteiras
│   │   └── operacao_models.py     # Modelos para operações
│   │
│   ├── routers/
│   │   ├── carteira_router.py     # Endpoints de carteiras
│   │   ├── movimentacao_router.py # Endpoints de depósito/saque
│   │   ├── conversao_router.py    # Endpoints de conversão
│   │   └── transferencia_router.py # Endpoints de transferência
│   │
│   ├── services/
│   │   ├── carteira_service.py
│   │   ├── movimentacao_service.py
│   │   ├── conversao_service.py
│   │   ├── transferencia_service.py
│   │   └── coinbase_service.py    # Integração com API Coinbase
│   │
│   └── persistence/
│       ├── db.py                  # Conexão com banco
│       └── repositories/
│           ├── carteira_repository.py
│           ├── movimentacao_repository.py
│           ├── conversao_repository.py
│           └── transferencia_repository.py
│
├── sql/
│   └── DDL_Carteira_Digital.sql   # Script de criação do banco
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 8. Subir a API

```bash
uvicorn api.main:app --reload
```

Acesse a documentação interativa:

👉 **http://127.0.0.1:8000/docs**

---

## 9. Endpoints Disponíveis

### 🔑 Carteiras

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/carteiras` | Cria nova carteira (retorna chave privada apenas uma vez) |
| GET | `/carteiras` | Lista todas as carteiras |
| GET | `/carteiras/{endereco}` | Busca carteira por endereço |
| DELETE | `/carteiras/{endereco}` | Bloqueia carteira |
| GET | `/carteiras/{endereco}/saldos` | Lista saldos em todas as moedas |

### 💰 Depósitos e Saques

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/carteiras/{endereco}/depositos` | Realiza depósito (sem taxa) |
| POST | `/carteiras/{endereco}/saques` | Realiza saque (requer chave privada + taxa) |

### 🔄 Conversão

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/carteiras/{endereco}/conversoes` | Converte entre moedas (usa API Coinbase + taxa) |

### 📤 Transferência

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/carteiras/{endereco_origem}/transferencias` | Transfere entre carteiras (taxa na origem) |

---

## 10. Exemplos de Uso

### Criar Carteira
```bash
curl -X POST http://localhost:8000/carteiras
```

**Resposta:**
```json
{
  "endereco_carteira": "a1b2c3d4...",
  "data_criacao": "2025-11-17T10:30:00",
  "status": "ATIVA",
  "chave_privada": "secret123..."
}
```

⚠️ **IMPORTANTE:** Guarde a `chave_privada`! Ela é retornada apenas uma vez.

---

### Ver Saldos
```bash
curl http://localhost:8000/carteiras/{endereco}/saldos
```

---

### Fazer Depósito
```bash
curl -X POST http://localhost:8000/carteiras/{endereco}/depositos \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_moeda": "BTC",
    "valor": 1.5
  }'
```

---

### Fazer Saque
```bash
curl -X POST http://localhost:8000/carteiras/{endereco}/saques \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_moeda": "BTC",
    "valor": 0.5,
    "chave_privada": "secret123..."
  }'
```

---

### Converter Moedas
```bash
curl -X POST http://localhost:8000/carteiras/{endereco}/conversoes \
  -H "Content-Type: application/json" \
  -d '{
    "moeda_origem": "BTC",
    "moeda_destino": "USD",
    "valor_origem": 0.1,
    "chave_privada": "secret123..."
  }'
```

---

### Transferir entre Carteiras
```bash
curl -X POST http://localhost:8000/carteiras/{endereco_origem}/transferencias \
  -H "Content-Type: application/json" \
  -d '{
    "endereco_destino": "xyz789...",
    "codigo_moeda": "BTC",
    "valor": 0.2,
    "chave_privada": "secret123..."
  }'
```

---

## 11. Segurança

- ✅ Chave privada armazenada apenas como **hash SHA-256**
- ✅ Validação de chave privada em operações sensíveis
- ✅ Verificação de saldo antes de saques/conversões/transferências
- ✅ Validação de status da carteira (bloqueada não pode operar)
- ✅ Usuário do banco com privilégios **apenas DML** (sem DDL)

---

## 12. Taxas Configuráveis

Todas as taxas são configuradas via `.env`:

- **TAXA_SAQUE**: Padrão 1% (0.01)
- **TAXA_CONVERSAO**: Padrão 2% (0.02)
- **TAXA_TRANSFERENCIA**: Padrão 1.5% (0.015)

---

## 13. Moedas Suportadas

| Código | Nome | Tipo |
|--------|------|------|
| BTC | Bitcoin | CRYPTO |
| ETH | Ethereum | CRYPTO |
| SOL | Solana | CRYPTO |
| USD | Dólar Americano | FIAT |
| BRL | Real Brasileiro | FIAT |

---

## 14. Problemas Comuns

### Erro de conexão com banco
- Verifique se o MySQL está rodando
- Confira as credenciais no `.env`
- Teste a conexão: `mysql -u wallet_api_homolog -papi123 wallet_homolog`

### Erro ao importar módulos
- Verifique se o venv está ativado
- Reinstale as dependências: `pip install -r requirements.txt`

### Erro na API Coinbase
- Verifique sua conexão com a internet
- Alguns pares de moedas podem não estar disponíveis

---

## 15. Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy Core** - Driver de conexão (sem ORM)
- **MySQL** - Banco de dados relacional
- **Pydantic** - Validação de dados
- **httpx** - Cliente HTTP assíncrono (Coinbase API)
- **python-dotenv** - Gerenciamento de variáveis de ambiente

---

## 16. Próximos Passos (Opcional)

- [ ] Adicionar autenticação JWT
- [ ] Implementar paginação nos endpoints de listagem
- [ ] Criar endpoint de histórico de transações
- [ ] Adicionar testes unitários
- [ ] Implementar cache para cotações
- [ ] Adicionar logs estruturados

---

## 17. Contribuindo

Este projeto é educacional. Sinta-se livre para:
- Reportar bugs
- Sugerir melhorias
- Fazer fork e experimentar

---

## 18. Licença

Projeto educacional - MIT License

---

## 19. Contato

Dúvidas sobre o projeto? Entre em contato através do GitHub!

---

**Boa implementação! 🚀**
