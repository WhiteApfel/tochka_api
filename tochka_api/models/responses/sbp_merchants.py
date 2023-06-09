from datetime import datetime

from models.responses import TochkaBaseResponse
from models.responses.sbp_legal import SbpMerchant
from pydantic import BaseModel, Field, root_validator


class SbpMerchantsResponse(TochkaBaseResponse):
    merchants: list[SbpMerchant] = Field(..., alias="MerchantList")

    @root_validator(pre=True)
    def one_merchant(cls, values: dict):
        if "contactPhoneNumber" in values["Data"]:
            values["MerchantList"] = [values["Data"]]
        return values


class SbpRegisterMerchantResponse(TochkaBaseResponse):
    merchant_id: str = Field(..., alias="merchantId")
