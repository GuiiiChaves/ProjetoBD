from fastapi import APIRouter, HTTPException, Depends

from api.services.conversao_service import ConversaoService
from api.services.coinbase_service import CoinbaseService
from api.persistence.repositories.conversao_repository import ConversaoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.operacao_models import ConversaoRequest, ConversaoResponse


router = APIRouter(tags=["conversões"])


def get_conversao_service() -> ConversaoService:
    conversao_repo = ConversaoRepository()
    carteira_repo = CarteiraRepository()
    coinbase_service = CoinbaseService()
    return ConversaoService(conversao_repo, carteira_repo, coinbase_service)


@router.post(
    "/carteiras/{endereco_carteira}/conversoes",
    response_model=ConversaoResponse,
    status_code=201
)
async def realizar_conversao(
    endereco_carteira: str,
    request: ConversaoRequest,
    service: ConversaoService = Depends(get_conversao_service),
):
    """
    Realiza conversão entre moedas.
    Requer chave privada, usa API Coinbase para cotação e possui taxa.
    """
    try:
        return await service.realizar_conversao(endereco_carteira, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
