import pytest

from models.responses.accounts import AccountsResponse


@pytest.mark.asyncio
async def test_accounts_response(tochka_client):
    response = await tochka_client.get_accounts()
    assert isinstance(response, AccountsResponse)


@pytest.mark.asyncio
async def test_account_response(tochka_client):
    accounts = await tochka_client.get_accounts()
    for account in accounts:
        response = await tochka_client.get_account(account.account_id)
        assert isinstance(response, AccountsResponse)
