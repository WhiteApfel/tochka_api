from datetime import datetime, timedelta
from pathlib import Path

import ujson
from pydantic import BaseModel, Field
from settings import HTTP_TIMEOUT


class Tokens(BaseModel):
    consents_token: str = None
    consents_expired_in: datetime = None
    access_token: str = None
    access_expired_in: datetime = None
    refresh_token: str = None
    path: Path = Field(None)
    allow_save_tokens: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.allow_save_tokens:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                loaded = self.load_tokens(self.path)
                self.consents_token = loaded.consents_token
                self.consents_expired_in = loaded.consents_expired_in
                self.access_token = loaded.access_token
                self.refresh_token = loaded.refresh_token
                self.access_expired_in = loaded.access_expired_in
            else:
                self.path.touch(exist_ok=True)
                self.save_tokens()

    def set_consents_token(self, token: str, expires_in: int):
        self.consents_token = token
        self.consents_expired_in = datetime.utcnow() + timedelta(
            seconds=expires_in - HTTP_TIMEOUT
        )
        self.save_tokens()

    def set_access_token(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.access_expired_in = datetime.utcnow() + timedelta(
            seconds=expires_in - HTTP_TIMEOUT
        )
        self.save_tokens()

    def save_tokens(self):
        if not self.allow_save_tokens:
            return
        self.path.write_text(
            self.json(
                include={
                    "consents_token",
                    "consents_expired_in",
                    "access_token",
                    "refresh_token",
                    "access_expired_in",
                    "allow_save_tokens",
                }
            )
        )

    @property
    def consents_is_alive(self) -> bool:
        return self.consents_expired_in > datetime.utcnow()

    @property
    def access_is_alive(self) -> bool:
        return self.access_expired_in > datetime.utcnow()

    @classmethod
    def load_tokens(cls, path):
        return cls(**(ujson.loads(path.read_text()) | {"allow_save_tokens": False}))
