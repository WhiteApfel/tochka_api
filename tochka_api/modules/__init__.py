# isort: off

from .base import TochkaAPIBase

# isort: on

from .accounts import TochkaAPIAccounts
from .balances import TochkaAPIBalances


class TochkaAPI(TochkaAPIBalances, TochkaAPIAccounts, TochkaAPIBase):
    ...
