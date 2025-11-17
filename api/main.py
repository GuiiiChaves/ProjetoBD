from fastapi import FastAPI
from api.routers.carteira_router import router as carteiras_router
from api.routers.movimentacao_router import router as movimentacao_router
from api.routers.conversao_router import router as conversao_router
from api.routers.transferencia_router import router as transferencia_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Carteira Digital API",
        version="1.0.0",
        description="API educacional de carteira digital com SQL puro e FastAPI.",
    )

    # Endpoint de teste (Mini-Sprint 1)
    @app.get("/", tags=["health"])
    def health_check():
        """Endpoint de teste para verificar se a API está funcionando"""
        return {
            "status": "ok",
            "message": "Carteira Digital API está funcionando!",
            "version": "1.0.0"
        }

    app.include_router(carteiras_router)
    app.include_router(movimentacao_router)
    app.include_router(conversao_router)
    app.include_router(transferencia_router)

    return app


app = create_app()


