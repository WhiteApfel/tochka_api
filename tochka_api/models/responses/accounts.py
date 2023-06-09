from datetime import date, datetime
from typing import Iterator, Literal

from models.responses import TochkaBaseResponse
from pydantic import BaseModel, Field, root_validator, validator


class AccountDetails(BaseModel):
    scheme: str = Field(..., alias="schemeName")
    identification: str
    name: str


class Account(BaseModel):
    customer_code: str = Field(..., alias="customerCode")
    account: str = Field(..., alias="accountId")
    transit_account: str | None = Field(None, alias="transitAccount")
    status: Literal["Enabled", "Disabled", "Deleted", "ProForma", "Pending"]
    status_updated_at: datetime = Field(..., alias="statusUpdateDateTime")
    currency: str
    account_type: Literal["Business", "Personal"] = Field(..., alias="accountType")
    account_sub_type: Literal[
        "CreditCard",
        "CurrentAccount",
        "Loan",
        "Mortgage",
        "PrePaidCard",
        "Savings",
        "Special",
    ] = Field(..., alias="accountSubType")
    registered_at: date = Field(..., alias="registrationDate")
    account_details: AccountDetails = Field(..., alias="accountDetails")

    @validator("account_details", pre=True)
    def normalize_account_details(cls, account_details):
        return account_details[0]


class AccountsResponse(TochkaBaseResponse):
    accounts: list[Account] = Field(..., alias="Account")

    @root_validator(pre=True)
    def one_account(cls, values: dict):
        if "transitAccount" in values["Data"]:
            values["Account"] = [values["Data"]]
        return values

    def __len__(self):
        return len(self.accounts)

    def __iter__(self) -> Iterator[Account]:
        if isinstance(self.accounts, list):
            return self.accounts.__iter__()
        return [self.accounts].__iter__()

    def __getitem__(self, item) -> Account:
        return self.accounts[item]
