from fastapi import APIRouter, HTTPException, Depends

from api.services.movimentacao_service import MovimentacaoService
from api.persistence.repositories.movimentacao_repository import MovimentacaoRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.operacao_models import (
    DepositoRequest,
    SaqueRequest,
    MovimentacaoResponse
)


router = APIRouter(tags=["movimentações"])


def get_movimentacao_service() -> MovimentacaoService:
    movimentacao_repo = MovimentacaoRepository()
    carteira_repo = CarteiraRepository()
    return MovimentacaoService(movimentacao_repo, carteira_repo)


@router.post(
    "/carteiras/{endereco_carteira}/depositos",
    response_model=MovimentacaoResponse,
    status_code=201
)
def realizar_deposito(
    endereco_carteira: str,
    request: DepositoRequest,
    service: MovimentacaoService = Depends(get_movimentacao_service),
):
    """
    Realiza um depósito na carteira.
    Não requer chave privada e não possui taxa.
    """
    try:
        return service.realizar_deposito(endereco_carteira, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/carteiras/{endereco_carteira}/saques",
    response_model=MovimentacaoResponse,
    status_code=201
)
def realizar_saque(
    endereco_carteira: str,
    request: SaqueRequest,
    service: MovimentacaoService = Depends(get_movimentacao_service),
):
    """
    Realiza um saque da carteira.
    Requer chave privada e possui taxa configurada via TAXA_SAQUE.
    """
    try:
        return service.realizar_saque(endereco_carteira, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
