from models.responses import SbpPaymentsResponse, SbpRefundResponse
from modules import TochkaApiBase


class TochkaApiSbpRefunds(TochkaApiBase):
    async def sbp_get_payments(
        self, customer_code: str, from_date: str, to_date: str
    ) -> SbpPaymentsResponse:
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/get-payments?customerCode={customer_code}&fromDate={from_date}&toDate={to_date}",
        )

    async def sbp_start_refund(
        self,
        account: str,
        amount: str,
        qrc: str,
        trx: str,
        currency: str = "RUB",
        bank_code: str = "044525999",
    ) -> SbpRefundResponse:
        data = {
            "Data": {
                "bankCode": bank_code,
                "accountCode": account,
                "amount": amount,
                "currency": currency,
                "qrcId": qrc,
                "refTransactionId": trx,
            }
        }
        return await self.request(
            method="POST",
            url="/sbp/v1.0/refund",
            json=data,
        )

    async def sbp_get_refund_data(self, request_id: str) -> SbpRefundResponse:
        return await self.request(method="GET", url=f"/sbp/v1.0/refund/{request_id}")
