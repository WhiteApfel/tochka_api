from datetime import datetime

import pytest as pytest
from models import Tokens
from settings import TOCHKA_SANDBOX_API_URL, TOCHKA_SANDBOX_VALID_TOKEN

from tochka_api import TochkaApi


@pytest.fixture
def tochka_client():
    tokens = Tokens()
    tokens.access_token = TOCHKA_SANDBOX_VALID_TOKEN
    tokens.access_expired_in = datetime(year=2042, month=12, day=31)
    client = TochkaApi("", "", base_url=TOCHKA_SANDBOX_API_URL, allow_save_tokens=False)
    client._tokens = tokens
    return client


@pytest.fixture
async def customer_code(tochka_client):
    accounts = await tochka_client.get_accounts()
    account = accounts[0]
    return account.customer_code


@pytest.fixture
async def legal_id(tochka_client, customer_code):
    customer_info = await tochka_client.sbp_get_customer_info(await customer_code)
    return customer_info.legal_id
