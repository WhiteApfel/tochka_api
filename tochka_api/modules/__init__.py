# isort: off

from .base import TochkaAPIBase

# isort: on

from .accounts import TochkaAPIAccounts
from .balances import TochkaAPIBalances
from .sbp_legal import TochkaApiSbpLegal


class TochkaAPI(TochkaApiSbpLegal, TochkaAPIBalances, TochkaAPIAccounts, TochkaAPIBase):
    ...
