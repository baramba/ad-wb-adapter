from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.http_validation_error import HTTPValidationError
from ...models.update_status_request import UpdateStatusRequest
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    x_user_id: str,
) -> Dict[str, Any]:
    url = "{}/v1/auth_data/check".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    headers["x-user-id"] = x_user_id

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
    }


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Optional[Union[HTTPValidationError, UpdateStatusRequest]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = UpdateStatusRequest.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, UpdateStatusRequest]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    x_user_id: str,
) -> Response[Union[HTTPValidationError, UpdateStatusRequest]]:
    """Метод для получения информации о наличии данных

     Метод возвращает информацию о наличии данных. Сами данные не возвращаются.

    Args:
        x_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, UpdateStatusRequest]]
    """

    kwargs = _get_kwargs(
        client=client,
        x_user_id=x_user_id,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Client,
    x_user_id: str,
) -> Optional[Union[HTTPValidationError, UpdateStatusRequest]]:
    """Метод для получения информации о наличии данных

     Метод возвращает информацию о наличии данных. Сами данные не возвращаются.

    Args:
        x_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, UpdateStatusRequest]
    """

    return sync_detailed(
        client=client,
        x_user_id=x_user_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    x_user_id: str,
) -> Response[Union[HTTPValidationError, UpdateStatusRequest]]:
    """Метод для получения информации о наличии данных

     Метод возвращает информацию о наличии данных. Сами данные не возвращаются.

    Args:
        x_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, UpdateStatusRequest]]
    """

    kwargs = _get_kwargs(
        client=client,
        x_user_id=x_user_id,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    x_user_id: str,
) -> Optional[Union[HTTPValidationError, UpdateStatusRequest]]:
    """Метод для получения информации о наличии данных

     Метод возвращает информацию о наличии данных. Сами данные не возвращаются.

    Args:
        x_user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, UpdateStatusRequest]
    """

    return (
        await asyncio_detailed(
            client=client,
            x_user_id=x_user_id,
        )
    ).parsed
