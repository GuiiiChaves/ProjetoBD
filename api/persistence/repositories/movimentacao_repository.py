import os
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy import text
from api.persistence.db import get_connection


class MovimentacaoRepository:
    """
    Repositório para depósitos e saques.
    """

    def realizar_deposito(
        self, 
        endereco_carteira: str, 
        codigo_moeda: str, 
        valor: Decimal
    ) -> Dict[str, Any]:
        """
        Realiza um depósito (sem taxa) e atualiza o saldo.
        """
        with get_connection() as conn:
            # 1) Registrar o depósito
            result = conn.execute(
                text("""
                    INSERT INTO deposito_saque 
                        (endereco_carteira, codigo_moeda, tipo, valor, taxa)
                    VALUES 
                        (:endereco, :moeda, 'DEPOSITO', :valor, 0)
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda": codigo_moeda,
                    "valor": valor
                },
            )
            deposito_id = result.lastrowid

            # 2) Atualizar saldo
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                       SET saldo = saldo + :valor
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda": codigo_moeda,
                    "valor": valor
                },
            )

            # 3) Buscar o registro criado
            row = conn.execute(
                text("""
                    SELECT id, endereco_carteira, codigo_moeda, tipo, 
                           valor, taxa, data_operacao
                      FROM deposito_saque
                     WHERE id = :id
                """),
                {"id": deposito_id},
            ).mappings().first()

        return dict(row)

    def realizar_saque(
        self, 
        endereco_carteira: str, 
        codigo_moeda: str, 
        valor: Decimal
    ) -> Dict[str, Any]:
        """
        Realiza um saque (com taxa) e atualiza o saldo.
        A taxa é configurada via variável de ambiente TAXA_SAQUE.
        """
        taxa_percentual = Decimal(os.getenv("TAXA_SAQUE", "0.01"))  # 1% padrão
        taxa = valor * taxa_percentual
        valor_total = valor + taxa

        with get_connection() as conn:
            # 1) Verificar saldo
            saldo_row = conn.execute(
                text("""
                    SELECT saldo
                      FROM saldo_carteira
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda
                """),
                {"endereco": endereco_carteira, "moeda": codigo_moeda},
            ).mappings().first()

            if not saldo_row or saldo_row["saldo"] < valor_total:
                raise ValueError("Saldo insuficiente para realizar o saque")

            # 2) Registrar o saque
            result = conn.execute(
                text("""
                    INSERT INTO deposito_saque 
                        (endereco_carteira, codigo_moeda, tipo, valor, taxa)
                    VALUES 
                        (:endereco, :moeda, 'SAQUE', :valor, :taxa)
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda": codigo_moeda,
                    "valor": valor,
                    "taxa": taxa
                },
            )
            saque_id = result.lastrowid

            # 3) Atualizar saldo (deduz valor + taxa)
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                       SET saldo = saldo - :valor_total
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda": codigo_moeda,
                    "valor_total": valor_total
                },
            )

            # 4) Buscar o registro criado
            row = conn.execute(
                text("""
                    SELECT id, endereco_carteira, codigo_moeda, tipo, 
                           valor, taxa, data_operacao
                      FROM deposito_saque
                     WHERE id = :id
                """),
                {"id": saque_id},
            ).mappings().first()

        return dict(row)
