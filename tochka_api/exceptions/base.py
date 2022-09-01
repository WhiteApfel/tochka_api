from httpx import Response


class TochkaError(BaseException):
    def __new__(cls, response: Response, *args, **kwargs):
        if response.status_code == 403:
            return super(TochkaError, TochkaUnauthorizedError).__new__(
                TochkaUnauthorizedError, response, *args, **kwargs
            )
        if response.status_code // 100 == 5:
            return super(TochkaError, TochkaServerError).__new__(
                TochkaServerError, response, *args, **kwargs
            )
        return super(TochkaError, cls).__new__(cls, response, *args, **kwargs)

    def __init__(self, response: Response, *args, **kwargs):
        self.status_code = response.status_code
        if "message" in response.text:
            self.text = response.json()["message"]
        else:
            self.text = response.text
        self.response = response
        super().__init__(f"(code={self.status_code}) {self.text}", *args)


class TochkaUnauthorizedError(TochkaError):
    ...


class TochkaServerError(TochkaError):
    ...
