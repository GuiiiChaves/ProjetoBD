from typing import List

from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.carteira_models import Carteira, CarteiraCriada
from api.models.operacao_models import Saldo


class CarteiraService:
    def __init__(self, carteira_repo: CarteiraRepository):
        self.carteira_repo = carteira_repo

    def criar_carteira(self) -> CarteiraCriada:
        row = self.carteira_repo.criar()
        # row tem: endereco_carteira, data_criacao, status, hash_chave_privada, chave_privada
        # não expomos o hash
        return CarteiraCriada(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
            chave_privada=row["chave_privada"],
        )

    def buscar_por_endereco(self, endereco_carteira: str) -> Carteira:
        row = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not row:
            raise ValueError("Carteira não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
        )

    def listar(self) -> List[Carteira]:
        rows = self.carteira_repo.listar()
        return [
            Carteira(
                endereco_carteira=r["endereco_carteira"],
                data_criacao=r["data_criacao"],
                status=r["status"],
            )
            for r in rows
        ]

    def bloquear(self, endereco_carteira: str) -> Carteira:
        row = self.carteira_repo.atualizar_status(endereco_carteira, "BLOQUEADA")
        if not row:
            raise ValueError("Carteira não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
        )

    def buscar_saldos(self, endereco_carteira: str) -> List[Saldo]:
        """Retorna todos os saldos da carteira"""
        # Primeiro verifica se a carteira existe
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError("Carteira não encontrada")
        
        rows = self.carteira_repo.buscar_saldos(endereco_carteira)
        return [
            Saldo(
                codigo_moeda=r["codigo_moeda"],
                nome_moeda=r["nome_moeda"],
                tipo_moeda=r["tipo_moeda"],
                saldo=r["saldo"],
            )
            for r in rows
        ]

    def validar_carteira_ativa(self, endereco_carteira: str) -> None:
        """Valida se a carteira existe e está ativa"""
        carteira = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not carteira:
            raise ValueError("Carteira não encontrada")
        if carteira["status"] != "ATIVA":
            raise ValueError("Carteira está bloqueada")
