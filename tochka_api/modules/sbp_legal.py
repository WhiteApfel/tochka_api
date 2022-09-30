from models.responses import (
    SbpCustomerInfoResponse,
    SbpLegalEntityResponse,
    SbpRegisterLegalEntity,
    TochkaBooleanResponse,
)
from models.responses.sbp_legal import SbpAccountsResponse
from modules import TochkaApiBase


class TochkaApiSbpLegal(TochkaApiBase):
    async def sbp_get_customer_info(
        self, customer_code: str
    ) -> SbpCustomerInfoResponse:
        return await self.request(
            method="GET", url=f"/sbp/v1.0/customer/{customer_code}"
        )

    async def sbp_get_legal_entity(self, legal_id: str) -> SbpLegalEntityResponse:
        return await self.request(
            method="GET", url=f"/sbp/v1.0/legal-entity/{legal_id}"
        )

    async def sbp_set_account_status(
        self, legal_id: str, account_id: str, active: str | bool = True
    ) -> TochkaBooleanResponse:
        data = {
            "Data": {
                "status": ("Active" if active else "Suspended")
                if type(active) is bool
                else active,
            }
        }
        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/account/{legal_id}/{account_id}",
            json=data,
        )

    async def sbp_set_legal_entity_status(
        self, legal_id: str, active: str | bool = True
    ) -> TochkaBooleanResponse:
        data = {
            "Data": {
                "status": ("Active" if active else "Suspended")
                if type(active) is bool
                else active,
            }
        }
        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/legal-entity/{legal_id}",
            json=data,
        )

    async def sbp_register_legal_entity(
        self, customer_code: str
    ) -> SbpRegisterLegalEntity:
        data = {
            "Data": {
                "customerCode": customer_code,
            }
        }

        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/register-legal-entity",
            json=data,
        )

    async def sbp_get_account(
        self, legal_id: str, account_id: str
    ) -> SbpAccountsResponse:
        return await self.request(
            method="GET", url=f"sbp/v1.0/account/{legal_id}/{account_id}"
        )

    async def sbp_get_accounts(self, legal_id: str) -> SbpAccountsResponse:
        return await self.request(method="GET", url=f"sbp/v1.0/account/{legal_id}")
