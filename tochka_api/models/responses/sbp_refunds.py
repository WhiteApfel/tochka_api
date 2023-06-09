from typing import Literal

from models.responses import TochkaBaseResponse
from pydantic import BaseModel, Field


class Payment(BaseModel):
    qrc_id: str = Field(..., alias="qrcId")
    status: Literal[
        "Confirming",
        "Confirmed",
        "Initiated",
        "Accepting",
        "Accepted",
        "InProgress",
        "Rejected",
        "Error",
        "Timeout",
    ]
    message: str
    trx_id: str = Field(..., alias="refTransactionId")


class SbpPaymentsResponse(TochkaBaseResponse):
    payments: list[Payment] = Field(..., alias="Payments")


class SbpRefundResponse(TochkaBaseResponse):
    request_id: str = Field(..., alias="requestId")
    status: Literal[
        "Initiated",
        "WaitingForConfirm",
        "Confirmed",
        "WaitingForAccept",
        "Accepted",
        "Rejected",
    ]
    description: str | None = Field(None, alias="statusDescription")
