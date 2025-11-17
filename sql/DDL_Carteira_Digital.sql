-- =========================================================
--  Script de criação da base, usuário,
--  Projeto: Carteira Digital
--  Banco:   MySQL 8+
-- =========================================================

-- 1) Criação da base de homologação
CREATE DATABASE IF NOT EXISTS wallet_homolog
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- 2) Criação do usuário restrito para a API
--    (ajuste a senha conforme necessário)
CREATE USER IF NOT EXISTS 'wallet_api_homolog'@'%'
    IDENTIFIED BY 'api123';

-- 3) Grants: apenas DML (sem CREATE/DROP/ALTER)
GRANT SELECT, INSERT, UPDATE, DELETE
    ON wallet_homolog.*
    TO 'wallet_api_homolog'@'%';

FLUSH PRIVILEGES;

-- 4) Usar a base
USE wallet_homolog;

-- =========================================================
--  Tabelas
-- =========================================================

-- Tabela de Carteiras
CREATE TABLE IF NOT EXISTS carteira (
    endereco_carteira VARCHAR(64) PRIMARY KEY,
    hash_chave_privada VARCHAR(64) NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ATIVA', 'BLOQUEADA') DEFAULT 'ATIVA'
);

-- Tabela de Moedas
CREATE TABLE IF NOT EXISTS moeda (
    codigo VARCHAR(10) PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    tipo ENUM('CRYPTO', 'FIAT') NOT NULL
);

-- Tabela de Saldos por Carteira
CREATE TABLE IF NOT EXISTS saldo_carteira (
    endereco_carteira VARCHAR(64) NOT NULL,
    codigo_moeda VARCHAR(10) NOT NULL,
    saldo DECIMAL(20, 8) NOT NULL DEFAULT 0,
    PRIMARY KEY (endereco_carteira, codigo_moeda),
    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (codigo_moeda) REFERENCES moeda(codigo)
);

-- Tabela de Depósitos e Saques
CREATE TABLE IF NOT EXISTS deposito_saque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(64) NOT NULL,
    codigo_moeda VARCHAR(10) NOT NULL,
    tipo ENUM('DEPOSITO', 'SAQUE') NOT NULL,
    valor DECIMAL(20, 8) NOT NULL,
    taxa DECIMAL(20, 8) DEFAULT 0,
    data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (codigo_moeda) REFERENCES moeda(codigo)
);

-- Tabela de Conversões
CREATE TABLE IF NOT EXISTS conversao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(64) NOT NULL,
    moeda_origem VARCHAR(10) NOT NULL,
    moeda_destino VARCHAR(10) NOT NULL,
    valor_origem DECIMAL(20, 8) NOT NULL,
    valor_destino DECIMAL(20, 8) NOT NULL,
    cotacao DECIMAL(20, 8) NOT NULL,
    taxa DECIMAL(20, 8) NOT NULL,
    data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (moeda_origem) REFERENCES moeda(codigo),
    FOREIGN KEY (moeda_destino) REFERENCES moeda(codigo)
);

-- Tabela de Transferências
CREATE TABLE IF NOT EXISTS transferencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endereco_origem VARCHAR(64) NOT NULL,
    endereco_destino VARCHAR(64) NOT NULL,
    codigo_moeda VARCHAR(10) NOT NULL,
    valor DECIMAL(20, 8) NOT NULL,
    taxa DECIMAL(20, 8) NOT NULL,
    data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (endereco_origem) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (endereco_destino) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (codigo_moeda) REFERENCES moeda(codigo)
);

-- Inserir moedas obrigatórias
INSERT INTO moeda (codigo, nome, tipo) VALUES
    ('BTC', 'Bitcoin', 'CRYPTO'),
    ('ETH', 'Ethereum', 'CRYPTO'),
    ('SOL', 'Solana', 'CRYPTO'),
    ('USD', 'Dólar Americano', 'FIAT'),
    ('BRL', 'Real Brasileiro', 'FIAT')
ON DUPLICATE KEY UPDATE nome=nome;