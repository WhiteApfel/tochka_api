from models.responses import SbpMerchantsResponse, SbpRegisterMerchantResponse, TochkaBooleanResponse
from modules import TochkaAPIBase


class TochkaApiSbpMerchant(TochkaAPIBase):
    async def sbp_get_merchants(self, legal_id: str) -> SbpMerchantsResponse:
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/merchant/legal-entity/{legal_id}",
        )

    async def sbp_get_merchant(self, merchant_id: str) -> SbpMerchantsResponse:
        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/merchant/{merchant_id}",
        )

    async def sbp_register_merchant(
        self,
        legal_id: str,
        name: str,
        mcc: str,
        address: str,
        city: str,
        region_code: str,
        zip_code: str,
        phone_number: str,
        country_code: str = "RU",
        capabilities: str = "011",
    ) -> SbpRegisterMerchantResponse:

        data = {
            "Data": {
                "address": address,
                "city": city,
                "countryCode": country_code,
                "countrySubDivisionCode": region_code,
                "zipCode": zip_code,
                "brandName": name,
                "capabilities": capabilities,
                "contactPhoneNumber": phone_number,
                "mcc": mcc,
            }
        }

        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/merchant/legal-entity/{legal_id}",
            json=data
        )

    async def sbp_set_merchant_status(self, merchant_id: str, is_active: bool | str = True) -> TochkaBooleanResponse:
        data = {
            "Data": {
                "status": ("Active" if is_active else "Suspended") if type(is_active) is bool else is_active,
            }
        }

        return await self.request(
            method="PUT",
            url=f"/sbp/v1.0/merchant/{merchant_id}",
            json=data
        )
