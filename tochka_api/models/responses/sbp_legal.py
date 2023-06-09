from datetime import datetime
from typing import Iterator, Literal

from models.responses import TochkaBaseResponse
from pydantic import BaseModel, Field, root_validator


class SbpLegalAddress(BaseModel):
    address: str | None
    city: str | None
    country_code: str = Field(..., alias="countryCode")
    region_code: str | None = Field(None, alias="countrySubDivisionCode")
    zip_code: str | None = Field(None, alias="zipCode")


class SbpLegalDetails(BaseModel):
    entity_type: str | None = Field(None, alias="entityType")
    inn: str
    kpp: str | None
    name: str
    ogrn: str


class SbpMerchant(SbpLegalAddress):
    status: Literal["Active", "Suspended"]
    created_at: datetime = Field(..., alias="createdAt")
    legal_id: str = Field(..., alias="legalId")
    merchant_id: str = Field(..., alias="merchantId")
    brand: str = Field(..., alias="brandName")
    capabilities: Literal["001", "010", "011"]
    phone: str | None = Field(None, alias="contactPhoneNumber")
    mcc: str
    additional_contacts: list[dict] | None = Field(None, alias="additionalContacts")


class SbpAccount(BaseModel):
    account: str = Field(..., alias="accountId")
    status: Literal["Active", "Suspended"]
    created_at: datetime = Field(..., alias="createdAt")
    legal_id: str = Field(..., alias="legalId")


class SbpCustomerInfoResponse(SbpLegalAddress, SbpLegalDetails, TochkaBaseResponse):
    """
    Refers to CustomerInfoResponseV3 https://enter.tochka.com/doc/v2/redoc/tag/swagger.json
    """

    status: Literal["Active", "Suspended"]
    created_at: datetime = Field(..., alias="createdAt")
    customer_code: str = Field(..., alias="customerCode")
    legal_id: str = Field(..., alias="legalId")
    merchants: list[SbpMerchant] = Field(..., alias="MerchantList")
    accounts: list[SbpAccount] = Field(..., alias="AccountList")


class SbpLegalEntityResponse(SbpLegalAddress, SbpLegalDetails, TochkaBaseResponse):
    status: Literal["Active", "Suspended"]
    created_at: datetime = Field(..., alias="createdAt")
    customer_code: str = Field(..., alias="customerCode")
    legal_id: str = Field(..., alias="legalId")


class SbpRegisterLegalEntityResponse(TochkaBaseResponse):
    legal_id: str = Field(..., alias="legalId")


class SbpAccountsResponse(TochkaBaseResponse):
    sbp_accounts: list[SbpAccount] = Field(..., alias="AccountList")

    @root_validator(pre=True)
    def one_account_to_list(cls, values: dict):  # noqa
        if "AccountList" not in values or "AccountList" not in values["Data"]:
            values["AccountList"] = [values["Data"]]
        return values

    def __len__(self):
        return len(self.sbp_accounts)

    def __iter__(self) -> Iterator[SbpAccount]:
        if isinstance(self.sbp_accounts, list):
            return self.sbp_accounts.__iter__()
        return [self.sbp_accounts].__iter__()

    def __getitem__(self, item) -> SbpAccount:
        return self.sbp_accounts[item]
