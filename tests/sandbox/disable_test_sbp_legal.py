import pytest
from models.responses import (
    SbpAccountsResponse,
    SbpCustomerInfoResponse,
    SbpLegalEntityResponse,
    SbpRegisterLegalEntity,
    TochkaBooleanResponse,
)


@pytest.mark.asyncio
async def test_sbp_get_customer_info(tochka_client, customer_code):
    response = await tochka_client.sbp_get_customer_info(await customer_code)
    assert isinstance(response, SbpCustomerInfoResponse)


@pytest.mark.asyncio
async def test_sbp_get_legal_entity(tochka_client, legal_id):
    response = await tochka_client.sbp_get_legal_entity(await legal_id)
    assert isinstance(response, SbpLegalEntityResponse)


@pytest.mark.asyncio
async def test_balance_response(tochka_client):
    accounts = await tochka_client.get_accounts()
    account = accounts[0]
    customer_info = await tochka_client.sbp_get_customer_info(account.customer_code)
    assert isinstance(customer_info, SbpCustomerInfoResponse)
    response = await tochka_client.sbp_get_legal_entity(customer_info.legal_id)
    assert isinstance(response, SbpLegalEntityResponse)


# async def sbp_set_account_status(
#         self, legal_id: str, account_id: str, active: str | bool = True
# ) -> TochkaBooleanResponse:
#     data = {
#         "Data": {
#             "status": ("Active" if active else "Suspended")
#             if type(active) is bool
#             else active,
#         }
#     }
#     return await self.request(
#         method="POST",
#         url=f"/sbp/v1.0/account/{legal_id}/{account_id}",
#         data=data,
#     )
#
#
# async def sbp_set_legal_entity_status(
#         self, legal_id: str, active: str | bool = True
# ) -> TochkaBooleanResponse:
#     data = {
#         "Data": {
#             "status": ("Active" if active else "Suspended")
#             if type(active) is bool
#             else active,
#         }
#     }
#     return await self.request(
#         method="POST",
#         url=f"/sbp/v1.0/legal-entity/{legal_id}",
#         data=data,
#     )
#
#
# async def sbp_register_legal_entity(self, customer_code: str) -> SbpRegisterLegalEntity:
#     data = {
#         "Data": {
#             "customerCode": customer_code,
#         }
#     }
#
#     return await self.request(
#         method="POST",
#         url=f"/sbp/v1.0/register-legal-entity",
#         data=data,
#     )
#
#
# async def sbp_get_account(self, legal_id: str, account_id: str) -> SbpAccountsResponse:
#     return await self.request(
#         method="GET",
#         url=f"sbp/v1.0/account/{legal_id}/{account_id}"
#     )
#
#
# async def sbp_get_accounts(self, legal_id: str) -> SbpAccountsResponse:
#     return await self.request(
#         method="GET",
#         url=f"sbp/v1.0/account/{legal_id}"
#     )
