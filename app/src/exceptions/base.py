from schemas.v1.base import ResponseCode, ResponseStatus


class WBAError(Exception):
    def __init__(
        self,
        *args: object,
        status_code: int = ResponseCode.ERROR,
        description: str | None = None,
    ) -> None:
        super().__init__(*args)
        self.status = ResponseStatus.ERROR
        self.status_code = status_code
        self.description = description


class WBAErrorNotAuth(Exception):
    def __init__(
        self,
        *args: object,
        status_code: int = ResponseCode.ERROR,
        description: str | None = None,
    ) -> None:
        super().__init__(*args)
        self.status = ResponseStatus.ERROR
        self.status_code = status_code
        self.description = description
