from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, root_validator, validator

from models.responses import TochkaBaseResponse


class SbpQrCodeImage(BaseModel):
    width: int
    height: int
    media_type: str = Field("image/png", alias="mediaType")
    content: str


class SbpQrCode(BaseModel):
    account_id: str = Field(..., alias="accountId")
    status: Literal["Active", "Suspended"]
    created_at: datetime = Field(..., alias="createdAt")
    qrc_id: str = Field(..., alias="qrcId")
    legal_id: str = Field(..., alias="legalId")
    merchant_id: str = Field(..., alias="merchantId")
    amount: int | None
    commission: float = Field(..., alias="commissionPercent")
    currency: str = "RUB"
    purpose: str | None = Field(None, alias="paymentPurpose")
    qrc_type: Literal["Static", "Dynamic"] = Field(..., alias="qrcType")
    version: str = Field(..., alias="templateVersion")
    payload: str
    source_name: str | None = Field(None, alias="sourceName")
    ttl: str | None
    image: SbpQrCodeImage

    @validator("qrc_type", pre=True)
    def normalize_qrc_type(cls, qrc_type: str):
        qrc_types = {
            "01": "Static",
            "02": "Dynamic",
        }
        return qrc_types[qrc_type]


class SbpQrsResponse(TochkaBaseResponse):
    codes: list[SbpQrCode] = Field(..., alias="qrCodeList")
