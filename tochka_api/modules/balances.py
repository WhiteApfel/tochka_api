from models.responses import BalanceResponse
from modules import TochkaAPIBase


class TochkaAPIBalances(TochkaAPIBase):
    async def get_balances(self) -> BalanceResponse:
        return await self.request(
            method="GET",
            url="/open-banking/v1.0/balances",
        )

    async def get_balance(self, account_id: str) -> BalanceResponse:
        return await self.request(
            method="GET",
            url=f"/open-banking/v1.0/accounts/{account_id}/balances",
        )
