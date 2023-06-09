import hashlib
from abc import ABC, abstractmethod
from base64 import b64decode, b64encode
from hashlib import md5
from pathlib import Path

import orjson as orjson
from appdirs import AppDirs
from Cryptodome.Cipher import AES
from models.tokens import Tokens


class AbstractTokenManager(ABC):
    def __init__(self, client_id: str, **kwargs):
        self.client_id = client_id
        self.tokens_mapper: dict[str, Tokens] = {}

    @abstractmethod
    def on_update(self, user_code: str, tokens_data: Tokens) -> None:
        ...

    @abstractmethod
    def get_tokens(
        self, user_code: str, allow_create: bool = False, **kwargs
    ) -> Tokens:
        ...

    @abstractmethod
    def load_tokens(self, **kwargs):
        ...


class InMemoryTokenManager(AbstractTokenManager):
    def __init__(self, client_id: str):
        super().__init__(client_id=client_id)

    def on_update(self, user_code: str, tokens_data: Tokens) -> None:
        pass

    def get_tokens(
        self, user_code: str, allow_create: bool = False, **kwargs
    ) -> Tokens:
        if allow_create:
            return self.tokens_mapper.setdefault(
                user_code, Tokens(user_code, self.on_update)
            )
        return self.tokens_mapper[user_code]

    def load_tokens(self, **kwargs):
        pass


class LocalStorageTokenManager(AbstractTokenManager):
    def __init__(self, client_id: str, tokens_path: str = None):
        super().__init__(client_id=client_id)

        self.json_dict = {}

        self.salt = md5(b"whiteapfel").hexdigest().encode()
        self.key = hashlib.scrypt(
            client_id.encode(), salt=self.salt, n=2, r=8, p=2, dklen=32
        )

        self.tokens_path = Path(tokens_path) if tokens_path is not None else None
        if self.tokens_path is None:
            app_dirs = AppDirs("tochka_api", "whiteapfel")
            self.tokens_path = Path(
                f"{app_dirs.user_data_dir}/{md5(self.client_id.encode()).hexdigest()}/tokens.json"
            )
            if not self.tokens_path.exists():
                self.tokens_path.parent.mkdir(exist_ok=True)
                self.tokens_path.touch()
                self.save_all()

    def get_cipher(self):
        return AES.new(self.key, AES.MODE_EAX, b64decode(b"GAYGAY0WHITEAPFELGAYEw=="))

    def save_all(self):
        json_string = orjson.dumps(self.json_dict)
        ciphertext, tag = self.get_cipher().encrypt_and_digest(json_string)
        encrypted_string = tag + ciphertext
        encoded_b64_string = b64encode(encrypted_string).decode()
        self.tokens_path.write_text(encoded_b64_string)

    def on_update(self, user_code: str, tokens_data: Tokens) -> None:
        self.json_dict[user_code] = tokens_data.dump()[1]
        self.save_all()

    def get_tokens(
        self, user_code: str, allow_create: bool = False, **kwargs
    ) -> Tokens:
        if allow_create:
            return self.tokens_mapper.setdefault(
                user_code, Tokens(user_code, self.on_update)
            )
        return self.tokens_mapper[user_code]

    def load_tokens(self, **kwargs):
        encoded_b64_string = self.tokens_path.read_text()
        encrypted_string = b64decode(encoded_b64_string)
        tag, ciphertext = encrypted_string[:16], encrypted_string[16:]
        json_string = self.get_cipher().decrypt_and_verify(ciphertext, tag)
        self.json_dict = orjson.loads(json_string)
        for user_code, tokens_data in self.json_dict.items():
            self.tokens_mapper[user_code] = Tokens(user_code, self.on_update)
            self.tokens_mapper[user_code].load(user_code, tokens_data)
