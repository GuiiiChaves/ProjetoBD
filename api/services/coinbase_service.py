import httpx
from decimal import Decimal
from typing import Dict


class CoinbaseService:
    """
    Serviço para consultar cotações na API pública da Coinbase.
    """
    BASE_URL = "https://api.coinbase.com/v2/prices"

    async def obter_cotacao(self, moeda_origem: str, moeda_destino: str) -> Decimal:
        """
        Obtém a cotação atual de moeda_origem para moeda_destino.
        Exemplo: BTC-USD retorna quanto vale 1 BTC em USD.
        """
        url = f"{self.BASE_URL}/{moeda_origem}-{moeda_destino}/spot"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # A API retorna: {"data": {"base": "BTC", "currency": "USD", "amount": "43250.00"}}
                amount = data.get("data", {}).get("amount")
                
                if not amount:
                    raise ValueError("Resposta da API Coinbase inválida")
                
                return Decimal(amount)
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ValueError(f"Par de moedas {moeda_origem}-{moeda_destino} não encontrado na Coinbase")
                raise ValueError(f"Erro ao consultar cotação: {e}")
            
            except Exception as e:
                raise ValueError(f"Erro ao obter cotação da Coinbase: {str(e)}")
