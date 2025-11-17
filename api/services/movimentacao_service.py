from decimal import Decimal
from typing import Dict, Any

from api.persistence.repositories.movimentacao_repository import MovimentacaoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.operacao_models import (
    DepositoRequest,
    SaqueRequest,
    MovimentacaoResponse
)


class MovimentacaoService:
    """
    Serviço para depósitos e saques.
    """

    def __init__(
        self,
        movimentacao_repo: MovimentacaoRepository,
        carteira_repo: CarteiraRepository
    ):
        self.movimentacao_repo = movimentacao_repo
        self.carteira_repo = carteira_repo

    def realizar_deposito(
        self,
        endereco_carteira: str,
        request: DepositoRequest
    ) -> MovimentacaoResponse:
        """
        Realiza depósito sem exigir chave privada.
        """
        # Valida se a carteira existe e está ativa
        self._validar_carteira_ativa(endereco_carteira)

        row = self.movimentacao_repo.realizar_deposito(
            endereco_carteira=endereco_carteira,
            codigo_moeda=request.codigo_moeda,
            valor=request.valor
        )

        return MovimentacaoResponse(**row)

    def realizar_saque(
        self,
        endereco_carteira: str,
        request: SaqueRequest
    ) -> MovimentacaoResponse:
        """
        Realiza saque com validação de chave privada e taxa.
        """
        # Valida se a carteira existe e está ativa
        self._validar_carteira_ativa(endereco_carteira)

        # Valida chave privada
        if not self.carteira_repo.validar_chave_privada(
            endereco_carteira, 
            request.chave_privada
        ):
            raise ValueError("Chave privada inválida")

        row = self.movimentacao_repo.realizar_saque(
            endereco_carteira=endereco_carteira,
            codigo_moeda=request.codigo_moeda,
            valor=request.valor
        )

        return MovimentacaoResponse(**row)

    def _validar_carteira_ativa(self, endereco_carteira: str) -> None:
        """Valida se a carteira existe e está ativa"""
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError("Carteira não encontrada")
        if carteira["status"] != "ATIVA":
            raise ValueError("Carteira está bloqueada")
