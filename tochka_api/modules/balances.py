from models.responses import BalanceResponse
from modules import TochkaApiBase


class TochkaApiBalances(TochkaApiBase):
    async def get_balances(self, user_code: str | None = None) -> BalanceResponse:
        return await self.request(
            method="GET",
            url="/open-banking/v1.0/balances",
        )

    async def get_balance(
        self, account: str, user_code: str | None = None
    ) -> BalanceResponse:
        return await self.request(
            method="GET",
            url=f"/open-banking/v1.0/accounts/{account}/balances",
        )
