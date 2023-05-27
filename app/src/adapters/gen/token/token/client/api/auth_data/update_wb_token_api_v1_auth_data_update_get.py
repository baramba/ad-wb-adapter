from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.http_validation_error import HTTPValidationError
from ...models.status_request import StatusRequest
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    user_id: str,
    wb_token_access: str,
) -> Dict[str, Any]:
    url = "{}/api/v1/auth_data/update".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["user_id"] = user_id

    params["wb_token_access"] = wb_token_access

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "params": params,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[HTTPValidationError, StatusRequest]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = StatusRequest.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[HTTPValidationError, StatusRequest]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    user_id: str,
    wb_token_access: str,
) -> Response[Union[HTTPValidationError, StatusRequest]]:
    """Метод для обновления wb_token

     Метод для запроса на обновление wb_token.

    Args:
        user_id (str):
        wb_token_access (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StatusRequest]]
    """

    kwargs = _get_kwargs(
        client=client,
        user_id=user_id,
        wb_token_access=wb_token_access,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    user_id: str,
    wb_token_access: str,
) -> Optional[Union[HTTPValidationError, StatusRequest]]:
    """Метод для обновления wb_token

     Метод для запроса на обновление wb_token.

    Args:
        user_id (str):
        wb_token_access (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StatusRequest]
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        wb_token_access=wb_token_access,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    user_id: str,
    wb_token_access: str,
) -> Response[Union[HTTPValidationError, StatusRequest]]:
    """Метод для обновления wb_token

     Метод для запроса на обновление wb_token.

    Args:
        user_id (str):
        wb_token_access (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StatusRequest]]
    """

    kwargs = _get_kwargs(
        client=client,
        user_id=user_id,
        wb_token_access=wb_token_access,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    user_id: str,
    wb_token_access: str,
) -> Optional[Union[HTTPValidationError, StatusRequest]]:
    """Метод для обновления wb_token

     Метод для запроса на обновление wb_token.

    Args:
        user_id (str):
        wb_token_access (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StatusRequest]
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            wb_token_access=wb_token_access,
        )
    ).parsed
