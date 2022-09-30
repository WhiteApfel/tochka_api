# isort: off

from .base import TochkaApiBase

# isort: on

from .accounts import TochkaApiAccounts
from .balances import TochkaApiBalances
from .sbp_legal import TochkaApiSbpLegal
from .sbp_merchant import TochkaApiSbpMerchant
from .sbp_qr import TochkaApiSbpQr
from .sbp_refunds import TochkaApiSbpRefunds


class TochkaAPI(
    TochkaApiSbpMerchant,
    TochkaApiSbpQr,
    TochkaApiSbpRefunds,
    TochkaApiSbpLegal,
    TochkaApiBalances,
    TochkaApiAccounts,
    TochkaApiBase,
):
    ...
