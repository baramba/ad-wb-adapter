from typing import Self

from schemas.v1.base import ResponseCode, ResponseStatus


class WBACampaignError(Exception):
    status_code: int

    @classmethod
    def init(cls, status_code: int, message: str) -> Self:
        result = cls(message)
        result.status_code = status_code
        return result


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
