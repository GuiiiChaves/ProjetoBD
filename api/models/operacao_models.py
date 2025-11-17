from decimal import Decimal
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


# ============ Modelos para Saldos ============
class Saldo(BaseModel):
    codigo_moeda: str
    nome_moeda: str
    tipo_moeda: Literal["CRYPTO", "FIAT"]
    saldo: Decimal


# ============ Modelos para Depósitos e Saques ============
class DepositoRequest(BaseModel):
    codigo_moeda: str = Field(..., description="Código da moeda (BTC, ETH, SOL, USD, BRL)")
    valor: Decimal = Field(..., gt=0, description="Valor a depositar")


class SaqueRequest(BaseModel):
    codigo_moeda: str = Field(..., description="Código da moeda (BTC, ETH, SOL, USD, BRL)")
    valor: Decimal = Field(..., gt=0, description="Valor a sacar")
    chave_privada: str = Field(..., description="Chave privada para autorização")


class MovimentacaoResponse(BaseModel):
    id: int
    endereco_carteira: str
    codigo_moeda: str
    tipo: Literal["DEPOSITO", "SAQUE"]
    valor: Decimal
    taxa: Decimal
    data_operacao: datetime


# ============ Modelos para Conversão ============
class ConversaoRequest(BaseModel):
    moeda_origem: str = Field(..., description="Código da moeda de origem")
    moeda_destino: str = Field(..., description="Código da moeda de destino")
    valor_origem: Decimal = Field(..., gt=0, description="Valor a converter")
    chave_privada: str = Field(..., description="Chave privada para autorização")


class ConversaoResponse(BaseModel):
    id: int
    endereco_carteira: str
    moeda_origem: str
    moeda_destino: str
    valor_origem: Decimal
    valor_destino: Decimal
    cotacao: Decimal
    taxa: Decimal
    data_operacao: datetime


# ============ Modelos para Transferência ============
class TransferenciaRequest(BaseModel):
    endereco_destino: str = Field(..., description="Endereço da carteira de destino")
    codigo_moeda: str = Field(..., description="Código da moeda")
    valor: Decimal = Field(..., gt=0, description="Valor a transferir")
    chave_privada: str = Field(..., description="Chave privada para autorização")


class TransferenciaResponse(BaseModel):
    id: int
    endereco_origem: str
    endereco_destino: str
    codigo_moeda: str
    valor: Decimal
    taxa: Decimal
    data_operacao: datetime
