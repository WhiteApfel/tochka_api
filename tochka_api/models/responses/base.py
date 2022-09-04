from pydantic import BaseModel, Field, root_validator


class TochkaBaseResponse(BaseModel):
    _valid_status_code: int = 200
    data: dict = Field(..., alias="Data", repr=False)
    links: dict = Field(..., alias="Links", repr=False)
    meta: dict = Field(..., alias="Meta", repr=False)

    @root_validator(pre=True)
    def unpack_data(cls, values: dict):  # noqa
        return values | values["Data"]


class TochkaBooleanResponse(TochkaBaseResponse):
    result: bool
