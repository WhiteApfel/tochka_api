from datetime import datetime
from decimal import Decimal
from typing import Literal

from models.responses import TochkaBaseResponse
from pydantic import BaseModel, Field, root_validator, validator


class Amount(BaseModel):
    total: Decimal = Field(..., alias="OpeningAvailable")
    available: Decimal = Field(..., alias="ClosingAvailable")
    hold: Decimal = Field(..., alias="Expected")


class Balance(BaseModel):
    account: str = Field(..., alias="accountId")
    indicator: Literal["Credit", "Debit"] = Field(..., alias="creditDebitIndicator")
    created_at: datetime = Field(..., alias="dateTime")
    currency: str
    amount: Amount


class BalanceResponse(TochkaBaseResponse):
    balances: list[Balance] | Balance = Field(..., alias="Balance")

    @validator(
        "balances",
        pre=True,
    )
    def normalize_balances(cls, balances: list):
        normalized_balances = {}
        for b in balances:
            if b["accountId"] not in normalized_balances:
                normalized_balances[b["accountId"]] = {
                    "accountId": b["accountId"],
                    "creditDebitIndicator": b["creditDebitIndicator"],
                    "dateTime": b["dateTime"],
                    "amount": {},
                }
            normalized_balances[b["accountId"]]["amount"][b["type"]] = b["Amount"][
                "amount"
            ]
            normalized_balances[b["accountId"]]["currency"] = b["Amount"]["currency"]
        if len(list(normalized_balances.keys())) == 1:
            return list(normalized_balances.values())[0]
        return list(normalized_balances.values())

    def __len__(self):
        return len(self.balances)

    def __iter__(self):
        if isinstance(self.balances, list):
            return self.balances.__iter__()
        return [self.balances].__iter__()

    def __getitem__(self, item):
        return self.balances[item]
