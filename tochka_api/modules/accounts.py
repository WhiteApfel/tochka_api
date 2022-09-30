from models.responses.accounts import AccountsResponse
from modules import TochkaApiBase


class TochkaApiAccounts(TochkaApiBase):
    async def get_accounts(self) -> AccountsResponse:
        return await self.request(
            method="GET",
            url="/open-banking/v1.0/accounts",
        )

    async def get_account(self, account_id: str) -> AccountsResponse:
        return await self.request(
            method="GET",
            url=f"/open-banking/v1.0/accounts/{account_id}",
        )
