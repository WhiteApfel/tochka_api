from datetime import datetime, timedelta, timezone
from typing import Callable

import dateutil.parser

from settings import HTTP_TIMEOUT


class TokenField(str):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, args[0])

    def __init__(
        self, value, *, expires_in: int | None = None, expires: datetime | None = None
    ):
        if expires is not None:
            self._expires = expires
        elif expires_in is None:
            self._expires = None
        else:
            self._expires = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in - HTTP_TIMEOUT
            )

    @property
    def expires(self) -> datetime | None:
        return self._expires

    @property
    def is_alive(self) -> bool:
        if self._expires is None:
            return True
        return datetime.now(timezone.utc) < self.expires


class TokenDescriptor:
    def __init__(self):
        self.value = None

    def __get__(self, instance, owner) -> TokenField | None:
        return self.value

    def __set__(
        self, instance, value: tuple[str, int | datetime | None, datetime | None] | str
    ):
        if type(value) is str:
            value = (value, None, None)
        elif len(value) == 1:
            value = value + (None, None)
        elif isinstance(value[1], datetime):
            value = (value[0], None, value[1])
        elif len(value) == 2:
            value = value + (None,)
        self.value = TokenField(value[0], expires_in=value[1], expires=value[2])

        instance.on_update(instance.user_code, instance)


class Tokens:
    __slots__ = ("on_update", "user_code")
    token_fields = ("client", "access", "refresh")
    client: TokenField | None = TokenDescriptor()
    access: TokenField | None = TokenDescriptor()
    refresh: TokenField | None = TokenDescriptor()

    def __init__(self, user_code, on_update: Callable[[str, dict], None]):
        self.on_update = on_update
        self.user_code = user_code
        # self.client: TokenField | None = TokenDescriptor()
        # self.access: TokenField | None = TokenDescriptor()
        # self.refresh: TokenField | None = TokenDescriptor()

    def dump(self) -> tuple[str, dict]:
        data = {}

        for field_name in self.token_fields:
            if field_name[0] == "_":
                continue

            field = getattr(self, field_name, None)

            data[field_name] = {
                "value": field,
                "expires": field.expires if field else None,
            }

        return self.user_code, data

    def load(self, user_code: str, data: dict[str, dict[str, str | datetime | None]]):
        self.user_code = user_code
        if not all(field in data for field in self.token_fields):
            raise ValueError("data does not contain all fields")

        for field_name in self.token_fields:
            field_data = data.get(field_name)
            value = field_data.get("value")
            expires = field_data.get("expires")
            if isinstance(expires, str):
                expires = dateutil.parser.parse(expires)
            setattr(self, field_name, (value, None, expires))
