import os
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy import text
from api.persistence.db import get_connection


class ConversaoRepository:
    """
    Repositório para conversões entre moedas.
    """

    def realizar_conversao(
        self,
        endereco_carteira: str,
        moeda_origem: str,
        moeda_destino: str,
        valor_origem: Decimal,
        cotacao: Decimal
    ) -> Dict[str, Any]:
        """
        Realiza conversão entre moedas com taxa.
        """
        taxa_percentual = Decimal(os.getenv("TAXA_CONVERSAO", "0.02"))  # 2% padrão
        
        # Calcula valor destino e taxa
        valor_bruto_destino = valor_origem * cotacao
        taxa = valor_bruto_destino * taxa_percentual
        valor_destino = valor_bruto_destino - taxa

        with get_connection() as conn:
            # 1) Verificar saldo origem
            saldo_row = conn.execute(
                text("""
                    SELECT saldo
                      FROM saldo_carteira
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda
                """),
                {"endereco": endereco_carteira, "moeda": moeda_origem},
            ).mappings().first()

            if not saldo_row or saldo_row["saldo"] < valor_origem:
                raise ValueError("Saldo insuficiente na moeda de origem")

            # 2) Registrar conversão
            result = conn.execute(
                text("""
                    INSERT INTO conversao 
                        (endereco_carteira, moeda_origem, moeda_destino, 
                         valor_origem, valor_destino, cotacao, taxa)
                    VALUES 
                        (:endereco, :moeda_origem, :moeda_destino, 
                         :valor_origem, :valor_destino, :cotacao, :taxa)
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda_origem": moeda_origem,
                    "moeda_destino": moeda_destino,
                    "valor_origem": valor_origem,
                    "valor_destino": valor_destino,
                    "cotacao": cotacao,
                    "taxa": taxa
                },
            )
            conversao_id = result.lastrowid

            # 3) Atualizar saldo origem (deduz)
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                       SET saldo = saldo - :valor_origem
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda_origem
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda_origem": moeda_origem,
                    "valor_origem": valor_origem
                },
            )

            # 4) Atualizar saldo destino (adiciona líquido)
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                       SET saldo = saldo + :valor_destino
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda_destino
                """),
                {
                    "endereco": endereco_carteira,
                    "moeda_destino": moeda_destino,
                    "valor_destino": valor_destino
                },
            )

            # 5) Buscar o registro criado
            row = conn.execute(
                text("""
                    SELECT id, endereco_carteira, moeda_origem, moeda_destino,
                           valor_origem, valor_destino, cotacao, taxa, data_operacao
                      FROM conversao
                     WHERE id = :id
                """),
                {"id": conversao_id},
            ).mappings().first()

        return dict(row)
