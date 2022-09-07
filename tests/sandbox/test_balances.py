import pytest
from models.responses import BalanceResponse


@pytest.mark.asyncio
async def test_balances_response(tochka_client):
    response = await tochka_client.get_balances()
    assert isinstance(response, BalanceResponse)


@pytest.mark.asyncio
async def test_balance_response(tochka_client):
    accounts = await tochka_client.get_accounts()
    for account in accounts:
        response = await tochka_client.get_balance(account_id=account.account_id)
        assert isinstance(response, BalanceResponse)
