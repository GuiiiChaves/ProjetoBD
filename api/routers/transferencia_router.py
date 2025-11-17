from fastapi import APIRouter, HTTPException, Depends

from api.services.transferencia_service import TransferenciaService
from api.persistence.repositories.transferencia_repository import TransferenciaRepository
from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.operacao_models import TransferenciaRequest, TransferenciaResponse


router = APIRouter(tags=["transferências"])


def get_transferencia_service() -> TransferenciaService:
    transferencia_repo = TransferenciaRepository()
    carteira_repo = CarteiraRepository()
    return TransferenciaService(transferencia_repo, carteira_repo)


@router.post(
    "/carteiras/{endereco_origem}/transferencias",
    response_model=TransferenciaResponse,
    status_code=201
)
def realizar_transferencia(
    endereco_origem: str,
    request: TransferenciaRequest,
    service: TransferenciaService = Depends(get_transferencia_service),
):
    """
    Realiza transferência entre carteiras.
    Requer chave privada da origem, possui taxa paga pela origem.
    Destino recebe o valor integral.
    """
    try:
        return service.realizar_transferencia(endereco_origem, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
