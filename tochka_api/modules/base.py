import inspect
import urllib.parse
from contextvars import ContextVar
from datetime import datetime, timedelta
from types import GenericAlias
from typing import Literal, Type

import jwt
import ujson as ujson
from exceptions.base import TochkaError
from httpx import AsyncClient, Response
from models import PermissionsEnum, Tokens
from models.responses import ConsentsResponse, TochkaBaseResponse
from settings import HTTP_TIMEOUT, TOCHKA_BASE_API_URL
from token_manager import (
    AbstractTokenManager,
    LocalStorageTokenManager,
)

context_user_code = ContextVar("context_user_code")


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
                        token = None
                        if f_kwargs.get("user_code") is not None:
                            token = context_user_code.set(f_kwargs.get("user_code"))
                        if (
                            "user_code" not in inspect.getfullargspec(f).args
                            and "user_code" in f_kwargs
                        ):
                            del f_kwargs["user_code"]
                        response: Response = await f(*f_args, **f_kwargs)

                        if token is not None:
                            context_user_code.reset(token)
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
        token_manager: Type[AbstractTokenManager] = LocalStorageTokenManager,
        one_customer_mode: bool = True,
        *args,
        **token_manager_data,
    ):
        self.__client_id: str = client_id
        self.__client_secret: str = client_secret
        self._base_url: str = base_url or TOCHKA_BASE_API_URL
        self.redirect_uri: str = redirect_uri

        self.token_manager: AbstractTokenManager = token_manager(
            self.__client_id, **token_manager_data
        )
        self.token_manager.load_tokens()
        self.one_customer_mode: bool = one_customer_mode
        self._user_code: str | None = None
        if self.one_customer_mode and len(self.token_manager.tokens_mapper) == 1:
            self._customer_code = list(self.token_manager.tokens_mapper.keys())[0]

        self._http_session: AsyncClient = None

    @property
    def http_session(self, user_code: str | None = None) -> AsyncClient:
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
        **get_tokens_params,
    ) -> Response:
        if json is not None:
            content = ujson.encode(json)
            headers = (headers or {}) | {"Content-Type": "application/json"}
        if auth_required:
            if self.one_customer_mode:
                get_tokens_params = get_tokens_params | {
                    "user_code": self._customer_code
                }
            else:
                get_tokens_params = get_tokens_params | {
                    "user_code": context_user_code.get()
                }
            tokens = self.token_manager.get_tokens(**get_tokens_params)
            if tokens.access is not None and not tokens.access.is_alive:
                await self.refresh_tokens(**get_tokens_params)
            elif tokens.access is None:
                raise ValueError("access_token is needed for authorization")
            headers = (headers or {}) | {"Authorization": f"Bearer {tokens.access}"}
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
            "scope": (
                "accounts balances customers statements cards sbp payments special"
            ),
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
            return response_data["access_token"], response_data["expires_in"]

        # TODO: Exception on error response

    async def create_consents(
        self,
        consents_token: str,
        permissions: list[PermissionsEnum],
        expires_in: int | timedelta = None,
        expiration_time: datetime = None,
    ) -> ConsentsResponse:
        data = {
            "Data": {
                "permissions": permissions,
            }
        }

        headers = {"Authorization": f"Bearer {consents_token}"}

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
        return (
            f"https://enter.tochka.com/connect/authorize?{'&'.join([f'{a}={b}' for a, b in params.items()])}"
        )

    async def get_access_token(
        self,
        code: str,
        token_id: str = None,
        customer_code: str = None,
        redirect_uri: str = None,
        **get_tokens_params,
    ) -> Tokens:
        if customer_code is None and token_id is None and customer_code is not None:
            raise ValueError(
                "`one_customer_mode=False` requires `customer_code` or `token_id` to be"
                " specified"
            )
        if token_id is not None and customer_code is None:
            token_data = jwt.decode(token_id, options={"verify_signature": False})
            customer_code = token_data["sub"]
        data = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "grant_type": "authorization_code",
            "scope": (
                "accounts balances customers statements cards sbp payments special"
            ),
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
            if self.one_customer_mode:
                self._customer_code = customer_code
            tokens = self.token_manager.get_tokens(
                customer_code, allow_create=True, **get_tokens_params
            )
            tokens.access = response_data["access_token"], response_data["expires_in"]
            tokens.refresh = response_data["refresh_token"], timedelta(days=30).seconds

            return tokens

        # TODO: сделать обработку исключений

    async def refresh_tokens(
        self,
        refresh_token: str | None = None,
        customer_code: str = None,
        **get_tokens_param,
    ) -> tuple[str, str, datetime]:
        tokens = None
        if refresh_token is None:
            if customer_code is None and not self.one_customer_mode:
                raise ValueError("`refresh_token` or `customer_code` is required")
            tokens = self.token_manager.get_tokens(
                customer_code or self._customer_code, **get_tokens_param
            )
            refresh_token = tokens.refresh

        data = {
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "grant_type": "refresh_token",
            "scope": "accounts",
            "refresh_token": refresh_token,
        }

        response = await self.request(
            method="POST",
            url="https://enter.tochka.com/connect/token",
            data=data,
            auth_required=False,
        )

        if response.status_code == 200:
            response_data = ujson.loads(response.text)
            access_token = response_data["access_token"]
            refresh_token = response_data["refresh_token"]
            expires_in = response_data["expires_in"]

            if tokens is not None:
                tokens.access = access_token, expires_in
                tokens.refresh = refresh_token, timedelta(days=30).seconds

            return (
                access_token,
                refresh_token,
                expires_in,
            )

        # TODO: сделать обработку исключений

    async def check_token(
        self,
        access_token: str | None = None,
        customer_code: str = None,
        **get_tokens_params,
    ) -> bool:
        if access_token is None:
            tokens = self.token_manager.get_tokens(customer_code, **get_tokens_params)
            access_token = tokens.access
        data = {
            "access_token": access_token,
        }

        response = await self.request(
            method="POST",
            url="https://enter.tochka.com/connect/introspect",
            data=data,
            auth_required=False,
        )

        return response.status_code == 200
