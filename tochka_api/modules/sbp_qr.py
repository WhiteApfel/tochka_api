from datetime import date
from typing import Literal

from models.responses import (
    SbpQrsResponse,
    SbpRegisterQrResponse,
    TochkaBooleanResponse,
    SbpQrPaymentDataResponse,
    SbpQrPaymentStatusResponse,
)
from modules import TochkaApiBase


class TochkaApiSbpQr(TochkaApiBase):
    async def sbp_get_qrs(self, legal_id: str) -> SbpQrsResponse:
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/qr-code/legal-entity/{legal_id}",
        )

    async def sbp_get_qr(self, qrc_id: str) -> SbpQrsResponse:
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/qr-code/{qrc_id}",
        )

    async def sbp_register_qr(
        self,
        merchant_id: str,
        account_id: str,
        is_static: bool | str = True,
        amount: int | None = None,
        currency: int | None = None,
        ttl: int | None = None,
        purpose: str = "",
        width: int = 300,
        height: int = 300,
        media_type: Literal["image/png", "image/svg+xml"] = "image/png",
    ) -> SbpRegisterQrResponse:
        data = {
            "Data": {
                "amount": amount,
                "currency": currency or "RUB",
                "paymentPurpose": purpose,
                "qrcType": ("01" if is_static else "02")
                if type(is_static) is bool
                else is_static,
                "imageParams": {
                    "width": width,
                    "height": height,
                    "media_type": media_type,
                },
                "sourceName": "whiteapfel/tochka_api",
                "ttl": ttl or 0,
            }
        }

        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/qr-code/merchant/{merchant_id}/{account_id}",
            json=data,
        )

    async def sbp_set_qr_status(
        self, qrc_id: str, is_active: bool | str = True
    ) -> TochkaBooleanResponse:
        data = {
            "Data": {
                "status": ("Active" if is_active else "Suspended")
                if type(is_active) is bool
                else is_active
            }
        }
        return await self.request(
            method="PUT",
            url=f"/sbp/v1.0/qr-code/{qrc_id}",
            json=data,
        )

    async def sbp_get_qr_payment_data(self, qrc_id: str) -> SbpQrPaymentDataResponse:
        return await self.request(
            method="GET", url=f"/sbp/v1.0/qr-code/{qrc_id}/payment-data"
        )

    async def sbp_get_qr_payment_status(
        self, qrc_id: str, from_date: date | None = None, to_date: date | None = None
    ) -> SbpQrPaymentStatusResponse:
        data = {}
        if from_date is not None:
            data["fromDate"] = from_date.strftime("%Y-%m-%d")
        if to_date is not None:
            data["toDate"] = to_date.strftime("%Y-%m-%d")
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/qr-code/{qrc_id}/payment-status",
            params=data,
        )
