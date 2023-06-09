from decimal import Decimal
from datetime import datetime
from typing import Literal

from models.responses import TochkaBaseResponse
from pydantic import BaseModel, Field, root_validator, validator


class SbpQrCodeImage(BaseModel):
    width: int
    height: int
    media_type: str = Field("image/png", alias="mediaType")
    content: str


class SbpQrCode(BaseModel):
    account: str = Field(..., alias="accountId")
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
    """
    Refers to QrCodePaymentDataV3

    Важно: атрибут ``amount`` вернёт сумму в рублях в формате ``Decimal``,
    для получения суммы в копейках надо обращаться к ``amount_raw``

    Важно: ``qrc_type`` имеет ENUM (01, 02) представление,
    для получения понятного представления надо обращаться к ``qrc_type_pretty``

    Пояснения к атрибуту ``scenario``:

    :param C2B_SUBSCRIPTION_WITH_PAYMENT: ссылка, зарегистрированная для Сценария «Оплата с привязкой счета»
    :param C2B_SUBSCRIPTION: ссылка, зарегистрированная для Сценария «Привязка счета без оплаты»
    :param C2B: одноразовая Платежная ссылка СБП или многоразовая Платежная ссылка СБП с фиксированной суммой
    :param C2B_CASH_REGISTER: кассовая Платежная ссылка СБП
    :param C2B_OPEN_SUM: многоразовая Платежная ссылка СБП с открытой суммой

    """

    address: str
    amount_raw: int or None = Field(..., alias="amount")
    currency: str or None
    brand_name: str = Field(..., alias="brandName")
    legal_name: str = Field(..., alias="legalName")
    payment_purpose: str | None = Field(..., alias="paymentPurpose")
    subscription_purpose: str | None = Field(..., alias="subscriptionPurpose")
    qrc_type: Literal["01", "02"] = Field(..., alias="qrcType")
    mcc: str
    qrc_id: str = Field(..., alias="qrcId")
    member_id: str = Field(..., alias="memberId")
    scenario: str

    ogrn: str | None
    inn: str | None

    redirect_url: str | None = Field(None, alias="redirectUrl")

    @property
    def amount(self) -> Decimal | None:
        if self.amount_raw is not None:
            return (Decimal(self.amount_raw) / Decimal(100)).quantize(Decimal("0.00"))
        return None

    @property
    def qrc_type_pretty(self) -> Literal["Static", "Dynamic"]:
        qrc_types = {
            "01": "Static",
            "02": "Dynamic",
        }
        return qrc_types[self.qrc_type]


class SbpQrPayment(BaseModel):
    qrc_id: str = Field(..., alias="qrcId")
    code: str
    status: Literal["NotStarted", "Received", "InProgress", "Accepted", "Rejected"]
    message: str
    trx_id: str | None = Field(None, alias="trxId")


class SbpQrPaymentStatusResponse(TochkaBaseResponse):
    payments: list[SbpQrPayment] = Field(..., alias="paymentList")
