# isort: off

from .base import TochkaAPIBase

# isort: on

from .accounts import TochkaAPIAccounts
from .balances import TochkaAPIBalances
from .sbp_legal import TochkaApiSbpLegal
from .sbp_refunds import TochkaApiSbpRefunds


class TochkaAPI(
    TochkaApiSbpRefunds,
    TochkaApiSbpLegal,
    TochkaAPIBalances,
    TochkaAPIAccounts,
    TochkaAPIBase,
):
    ...
