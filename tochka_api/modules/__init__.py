# isort: off

from .base import TochkaAPIBase

# isort: on

from .accounts import TochkaAPIAccounts
from .balances import TochkaAPIBalances
from .sbp_legal import TochkaApiSbpLegal
from .sbp_merchant import TochkaApiSbpMerchant
from .sbp_qr import TochkaApiSbpQr
from .sbp_refunds import TochkaApiSbpRefunds


class TochkaAPI(
    TochkaApiSbpMerchant,
    TochkaApiSbpQr,
    TochkaApiSbpRefunds,
    TochkaApiSbpLegal,
    TochkaAPIBalances,
    TochkaAPIAccounts,
    TochkaAPIBase,
):
    ...
