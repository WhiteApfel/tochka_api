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

    @root_validator(pre=True)
    def one_qr(cls, values: dict):
        if "qrcId" in values["Data"]:
            values["Account"] = [values["Data"]]
        return values


class SbpQrsResponse(TochkaBaseResponse):
    codes: list[SbpQrCode] = Field(..., alias="qrCodeList")


class SbpRegisterQrResponse(TochkaBaseResponse):
    qrc_id: str = Field(..., alias="qrcId")
    payload: str
    image: SbpQrCodeImage


class SbpQrPaymentDataResponse(TochkaBaseResponse):
    address: str
    amount: int or None
    currency: str or None
    brand_name: str = Field(..., alias="brandName")
    legal_name: str = Field(..., alias="legalName")
    payment_purpose: str | None = Field(..., alias="paymentPurpose")
    qrc_type: str
    mcc: str
    crc: str
    qrc_id: str = Field(..., alias="qrcId")
    creditor_bank_id: str = Field(..., alias="creditorBankId")

    @validator("qrc_type", pre=True)
    def normalize_qrc_type(cls, qrc_type: str):
        qrc_types = {
            "01": "Static",
            "02": "Dynamic",
        }
        return qrc_types[qrc_type]


class SbpQrPayment(BaseModel):
    qrc_id: str = Field(..., alias="qrcId")
    code: str
    status: Literal["NotStarted", "Received", "InProgress", "Accepted", "Rejected"]
    message: str
    trx_id: str | None = Field(None, alias="trxId")


class SbpQrPaymentStatusResponse(TochkaBaseResponse):
    payments: list[SbpQrPayment] = Field(..., alias="paymentList")
