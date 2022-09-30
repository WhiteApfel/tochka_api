import inspect
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from types import GenericAlias
from typing import Literal

import ujson as ujson
from appdirs import AppDirs
from exceptions.base import TochkaError
from httpx import AsyncClient, Response
from models import PermissionsEnum, Tokens
from models.responses import ConsentsResponse, TochkaBaseResponse
from settings import HTTP_TIMEOUT, TOCHKA_BASE_API_URL


class TochkaAPIMeta:
    def __new__(cls, *args, **kwargs):
        for name, function in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith("__"):
                continue
            if (
                "return" in function.__annotations__
                and isinstance(function.__annotations__["return"], type)
                and not isinstance(function.__annotations__["return"], GenericAlias)
                and issubclass(function.__annotations__["return"], TochkaBaseResponse)
            ):

                def decorate(f):
                    async def decorated(*f_args, **f_kwargs):
                        response: Response = await f(*f_args, **f_kwargs)
                        if (
                            response.status_code
                            == f.__annotations__["return"]._valid_status_code
                        ):
                            return f.__annotations__["return"](
                                **ujson.loads(response.text)
                            )
                        else:
                            raise TochkaError(response)

                    return decorated

                setattr(cls, name, decorate(function))

        return super(TochkaAPIMeta, cls).__new__(cls)


class TochkaApiBase(TochkaAPIMeta):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str | None = None,
        redirect_uri: str | None = None,
        tokens_path: str | None = None,
        allow_save_tokens: bool = True,
        *args,
        **kwargs,
    ):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.redirect_uri = redirect_uri
        self._allow_save_tokens = allow_save_tokens
        self._base_url = base_url or TOCHKA_BASE_API_URL
        self._tokens_path = Path(tokens_path) if tokens_path is not None else None
        if self._tokens_path is None:
            self._app_dirs = AppDirs("tochka_api", "whiteapfel")
            self.tokens_path = Path(
                f"{self._app_dirs.user_data_dir}/{self.__client_id}/tokens.json"
            )
        self._tokens: Tokens | None = None
        self._http_session: AsyncClient = None

    @property
    def tokens(self):
        if self._tokens is None:
            if self._allow_save_tokens:
                self._tokens = Tokens(path=self.tokens_path, allow_save_tokens=True)
            else:
                self._tokens = Tokens()
        return self._tokens

    @property
    def http_session(self) -> AsyncClient:
        if self._http_session is None:
            self._http_session = AsyncClient()
        return self._http_session

    async def request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        url: str = "",
        headers: dict = None,
        json: dict = None,
        data: dict = None,
        params: dict = None,
        cookies: dict = None,
        content: bytes = None,
        auth_required: bool = True,
    ) -> Response:
        if json is not None:
            content = ujson.encode(json)
            headers = (headers or {}) | {"Content-Type": "application/json"}
        if auth_required:
            if self.tokens.access_token is not None and not self.tokens.access_is_alive:
                await self.refresh_tokens()
            elif self.tokens.access_token is None:
                raise ValueError("access_token is needed for authorization")
            headers = (headers or {}) | {
                "Authorization": f"Bearer {self.tokens.access_token}"
            }
        return await self.http_session.request(
            method=method,
            url=url if url.startswith("https://") else self._base_url + url,
            data=data,
            headers=headers,
            params=params,
            cookies=cookies,
            timeout=HTTP_TIMEOUT,
            content=content,
        )

    async def get_consents_token(self) -> tuple[str, datetime]:
        data = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "grant_type": "client_credentials",
            "scope": "accounts",
            "state": "qwe",
        }
        response = await self.request(
            method="POST",
            url="https://enter.tochka.com/connect/token",
            data=data,
            auth_required=False,
        )

        if response.status_code == 200:
            response_data = ujson.loads(response.text)
            self.tokens.set_consents_token(
                token=response_data["access_token"],
                expires_in=response_data["expires_in"],
            )
            return self.tokens.consents_token, self.tokens.consents_expired_in

        # TODO: Exception on error response

    async def create_consents(
        self,
        permissions: list[PermissionsEnum],
        expires_in: int | timedelta = None,
        expiration_time: datetime = None,
    ) -> ConsentsResponse:
        data = {
            "Data": {
                "permissions": permissions,
            }
        }

        headers = {"Authorization": f"Bearer {self.tokens.consents_token}"}

        if expiration_time is not None or expires_in is not None:
            if expiration_time is None:
                if isinstance(expires_in, int):
                    expires_in = timedelta(seconds=expires_in)
                expiration_time = datetime.now() + expires_in
            data["Data"]["expirationDateTime"] = expiration_time.strftime(
                "%Y-%m-%dT%H:%M:%S%z",  # 2020-10-03T00:00:00+00:00
            )

        return await self.request(
            method="POST",
            url="/v1.0/consents",
            json=data,
            headers=headers,
            auth_required=False,
        )

    def generate_auth_url(
        self,
        consent_id: str,
        redirect_uri: str = None,
        response_type: Literal["code", "code id_token"] = "code id_token",
        scope: str = "accounts cards customers sbp payments",
        state: str | None = None,
    ) -> str:
        params = {
            "client_id": self.__client_id,
            "response_type": urllib.parse.quote(response_type),
            "redirect_uri": redirect_uri or self.redirect_uri,
            "scope": urllib.parse.quote(scope),
            "consent_id": consent_id,
        }
        if state is not None:
            params["state"] = urllib.parse.quote(state)
        return f"https://enter.tochka.com/connect/authorize?{'&'.join([f'{a}={b}' for a, b in params.items()])}"

    async def get_access_token(
        self, code: str, redirect_uri: str = None
    ) -> tuple[str, str, datetime]:
        data = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "grant_type": "authorization_code",
            "scope": "accounts",
            "code": code,
            "redirect_uri": redirect_uri or self.redirect_uri,
        }

        response = await self.request(
            method="POST",
            url="https://enter.tochka.com/connect/token",
            data=data,
            auth_required=False,
        )

        if response.status_code == 200:
            response_data = ujson.loads(response.text)
            self.tokens.set_access_token(
                access_token=response_data["access_token"],
                refresh_token=response_data["refresh_token"],
                expires_in=response_data["expires_in"],
            )
            return (
                self.tokens.access_token,
                self.tokens.refresh_token,
                self.tokens.consents_expired_in,
            )

        # TODO: сделать обработку исключений

    async def refresh_tokens(
        self, refresh_token: str | None = None
    ) -> tuple[str, str, datetime]:
        data = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "grant_type": "refresh_token",
            "scope": "accounts",
            "refresh_token": refresh_token or self.tokens.refresh_token,
        }

        response = await self.request(
            method="POST",
            url="https://enter.tochka.com/connect/token",
            data=data,
            auth_required=False,
        )

        if response.status_code == 200:
            response_data = ujson.loads(response.text)
            self.tokens.set_access_token(
                access_token=response_data["access_token"],
                refresh_token=response_data["refresh_token"],
                expires_in=response_data["expires_in"],
            )
            return (
                self.tokens.access_token,
                self.tokens.refresh_token,
                self.tokens.consents_expired_in,
            )

        # TODO: сделать обработку исключений

    async def check_token(self, access_token: str | None = None) -> bool:
        data = {
            "access_token": access_token or self.tokens.access_token,
        }

        response = await self.request(
            method="POST",
            url="https://enter.tochka.com/connect/introspect",
            data=data,
            auth_required=False,
        )

        return response.status_code == 200
