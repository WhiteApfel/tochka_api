from datetime import datetime

from models import PermissionsEnum
from models.responses import TochkaBaseResponse
from pydantic import Field


class ConsentsResponse(TochkaBaseResponse):
    status: str
    created_at: datetime = Field(..., alias="creationDateTime")
    updated_at: datetime = Field(..., alias="statusUpdateDateTime")
    permissions: list[PermissionsEnum]
    expiration_time: datetime | None = Field(None, alias="expirationDateTime")
    consent_id: str = Field(..., alias="consentId")
    customer_code: str | None = Field(None, alias="customerCode")
    app_name: str | None = Field(..., alias="applicationName")
    consumer_id: str = Field(..., alias="consumerId")
    client_id: str = Field(..., alias="clientId")
