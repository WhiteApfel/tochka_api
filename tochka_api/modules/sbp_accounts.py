from models.responses import SbpAccountsResponse, TochkaBooleanResponse
from modules import TochkaApiBase


class TochkaAPISbpAccounts(TochkaApiBase):
    async def sbp_get_accounts(self, legal_id: str) -> SbpAccountsResponse:
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/account/{legal_id}",
        )

    async def sbp_get_account(self, legal_id: str, account_id: str):
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/account/{legal_id}/{account_id}",
        )

    async def sbp_set_account_status(
        self, legal_id: str, account_id: str, is_active: bool | str = True
    ) -> TochkaBooleanResponse:
        data = {
            "Data": {
                "status": ("Active" if is_active else "Suspended")
                if type(is_active) is bool
                else is_active
            }
        }
        return await self.request(
            method="PUT",
            url=f"/sbp/v1.0/account/{legal_id}/{account_id}",
            json=data,
        )

    async def sbp_register_account(self, legal_id: str, account_id: str) -> TochkaBooleanResponse:
        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/account/{legal_id}/{account_id}",
        )
