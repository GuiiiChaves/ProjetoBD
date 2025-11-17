from decimal import Decimal

from api.persistence.repositories.conversao_repository import ConversaoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.services.coinbase_service import CoinbaseService
from api.models.operacao_models import ConversaoRequest, ConversaoResponse


class ConversaoService:
    """
    Serviço para conversão entre moedas.
    """

    def __init__(
        self,
        conversao_repo: ConversaoRepository,
        carteira_repo: CarteiraRepository,
        coinbase_service: CoinbaseService
    ):
        self.conversao_repo = conversao_repo
        self.carteira_repo = carteira_repo
        self.coinbase_service = coinbase_service

    async def realizar_conversao(
        self,
        endereco_carteira: str,
        request: ConversaoRequest
    ) -> ConversaoResponse:
        """
        Realiza conversão entre moedas com validação de chave privada.
        """
        # Valida se a carteira existe e está ativa
        self._validar_carteira_ativa(endereco_carteira)

        # Valida chave privada
        if not self.carteira_repo.validar_chave_privada(
            endereco_carteira,
            request.chave_privada
        ):
            raise ValueError("Chave privada inválida")

        # Valida se moedas são diferentes
        if request.moeda_origem == request.moeda_destino:
            raise ValueError("Moedas de origem e destino devem ser diferentes")

        # Obtém cotação da Coinbase
        cotacao = await self.coinbase_service.obter_cotacao(
            request.moeda_origem,
            request.moeda_destino
        )

        # Realiza conversão
        row = self.conversao_repo.realizar_conversao(
            endereco_carteira=endereco_carteira,
            moeda_origem=request.moeda_origem,
            moeda_destino=request.moeda_destino,
            valor_origem=request.valor_origem,
            cotacao=cotacao
        )

        return ConversaoResponse(**row)

    def _validar_carteira_ativa(self, endereco_carteira: str) -> None:
        """Valida se a carteira existe e está ativa"""
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError("Carteira não encontrada")
        if carteira["status"] != "ATIVA":
            raise ValueError("Carteira está bloqueada")
