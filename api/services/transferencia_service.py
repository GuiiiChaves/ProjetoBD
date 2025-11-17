from api.persistence.repositories.transferencia_repository import TransferenciaRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.operacao_models import TransferenciaRequest, TransferenciaResponse


class TransferenciaService:
    """
    Serviço para transferências entre carteiras.
    """

    def __init__(
        self,
        transferencia_repo: TransferenciaRepository,
        carteira_repo: CarteiraRepository
    ):
        self.transferencia_repo = transferencia_repo
        self.carteira_repo = carteira_repo

    def realizar_transferencia(
        self,
        endereco_origem: str,
        request: TransferenciaRequest
    ) -> TransferenciaResponse:
        """
        Realiza transferência entre carteiras com validação de chave privada.
        """
        # Valida se a carteira origem existe e está ativa
        self._validar_carteira_ativa(endereco_origem)

        # Valida chave privada
        if not self.carteira_repo.validar_chave_privada(
            endereco_origem,
            request.chave_privada
        ):
            raise ValueError("Chave privada inválida")

        # Valida se origem e destino são diferentes
        if endereco_origem == request.endereco_destino:
            raise ValueError("Origem e destino devem ser diferentes")

        # Realiza transferência (o repository valida a carteira destino)
        row = self.transferencia_repo.realizar_transferencia(
            endereco_origem=endereco_origem,
            endereco_destino=request.endereco_destino,
            codigo_moeda=request.codigo_moeda,
            valor=request.valor
        )

        return TransferenciaResponse(**row)

    def _validar_carteira_ativa(self, endereco_carteira: str) -> None:
        """Valida se a carteira existe e está ativa"""
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError("Carteira não encontrada")
        if carteira["status"] != "ATIVA":
            raise ValueError("Carteira está bloqueada")
