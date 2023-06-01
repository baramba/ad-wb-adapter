from http import HTTPStatus

from exceptions.base import WBAError, WBAErrorNotAuth


def error_for_raise(
    status_code: int,
    description: str,
    error_class: type[WBAError],
) -> WBAErrorNotAuth | WBAError:
    error: Exception = Exception()
    if status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
        return WBAErrorNotAuth(
            status_code=status_code,
            description=description,
        )

    error = error_class(
        status_code=status_code,
        description=description,
    )
    return error
