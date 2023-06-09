from models.responses import TochkaBaseResponse
from models.responses.sbp_legal import SbpAccount
from pydantic import BaseModel, Field, root_validator


class SbpAccountsResponse(TochkaBaseResponse):
    accounts: list[SbpAccount] = Field(..., alias="AccountList")

    @root_validator(pre=True)
    def one_account(cls, values: dict):
        if "accountId" in values["Data"]:
            values["AccountList"] = [values["Data"]]
        return values
