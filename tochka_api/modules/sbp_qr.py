from models.responses import SbpQrsResponse
from modules import TochkaAPIBase


class TochkaApiSbpQr(TochkaAPIBase):
    async def sbp_get_qrs(self, legal_id: str) -> SbpQrsResponse:
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/qr-code/legal-entity/{legal_id}",
        )

    async def sbp_register_qrc(
        self,
        merchant_id: str,
        is_static: bool | str = True,
        purpose: str = "",
        amount: int | None = None,
        currency: int | None = None,
        ttl: int | None = None,
        width: int = 300,
        height: int = 300,
        media_type: str = "image/png",
    ):
        data = {
            "Data": {
                "amount": 0,
                "currency": "RUB",
                "paymentPurpose": "?",
                "qrcType": ("01" if is_static else "02") if type(is_static) is bool else is_static,
                "imageParams": {
                    "width": width,
                    "height": height,
                    "media_type":
                },
                "sourceName": "string",
                "ttl": 0
            }
        }

