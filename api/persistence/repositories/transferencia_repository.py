import os
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy import text
from api.persistence.db import get_connection


class TransferenciaRepository:
    """
    Repositório para transferências entre carteiras.
    """

    def realizar_transferencia(
        self,
        endereco_origem: str,
        endereco_destino: str,
        codigo_moeda: str,
        valor: Decimal
    ) -> Dict[str, Any]:
        """
        Realiza transferência entre carteiras.
        A carteira origem paga a taxa, a destino recebe o valor integral.
        """
        taxa_percentual = Decimal(os.getenv("TAXA_TRANSFERENCIA", "0.015"))  # 1.5% padrão
        taxa = valor * taxa_percentual
        valor_total = valor + taxa

        with get_connection() as conn:
            # 1) Verificar se carteira destino existe e está ativa
            dest_row = conn.execute(
                text("""
                    SELECT status
                      FROM carteira
                     WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_destino},
            ).mappings().first()

            if not dest_row:
                raise ValueError("Carteira de destino não encontrada")
            
            if dest_row["status"] != "ATIVA":
                raise ValueError("Carteira de destino está bloqueada")

            # 2) Verificar saldo origem
            saldo_row = conn.execute(
                text("""
                    SELECT saldo
                      FROM saldo_carteira
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda
                """),
                {"endereco": endereco_origem, "moeda": codigo_moeda},
            ).mappings().first()

            if not saldo_row or saldo_row["saldo"] < valor_total:
                raise ValueError("Saldo insuficiente para realizar a transferência")

            # 3) Registrar transferência
            result = conn.execute(
                text("""
                    INSERT INTO transferencia 
                        (endereco_origem, endereco_destino, codigo_moeda, valor, taxa)
                    VALUES 
                        (:origem, :destino, :moeda, :valor, :taxa)
                """),
                {
                    "origem": endereco_origem,
                    "destino": endereco_destino,
                    "moeda": codigo_moeda,
                    "valor": valor,
                    "taxa": taxa
                },
            )
            transferencia_id = result.lastrowid

            # 4) Atualizar saldo origem (deduz valor + taxa)
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                       SET saldo = saldo - :valor_total
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda
                """),
                {
                    "endereco": endereco_origem,
                    "moeda": codigo_moeda,
                    "valor_total": valor_total
                },
            )

            # 5) Atualizar saldo destino (adiciona apenas o valor, sem taxa)
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                       SET saldo = saldo + :valor
                     WHERE endereco_carteira = :endereco
                       AND codigo_moeda = :moeda
                """),
                {
                    "endereco": endereco_destino,
                    "moeda": codigo_moeda,
                    "valor": valor
                },
            )

            # 6) Buscar o registro criado
            row = conn.execute(
                text("""
                    SELECT id, endereco_origem, endereco_destino, codigo_moeda,
                           valor, taxa, data_operacao
                      FROM transferencia
                     WHERE id = :id
                """),
                {"id": transferencia_id},
            ).mappings().first()

        return dict(row)
