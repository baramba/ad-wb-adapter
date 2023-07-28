from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import Client
from ...models.create_auth_data import CreateAuthData
from ...models.http_validation_error import HTTPValidationError
from ...models.status_request import StatusRequest
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: CreateAuthData,
    x_user_id: str,
) -> Dict[str, Any]:
    url = "{}/v1/auth_data".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    headers["x-user-id"] = x_user_id

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "follow_redirects": client.follow_redirects,
        "json": json_json_body,
    }


def _parse_response(*, client: Client, response: httpx.Response) -> Optional[Union[HTTPValidationError, StatusRequest]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = StatusRequest.from_dict(response.json())

        return response_201
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[HTTPValidationError, StatusRequest]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: CreateAuthData,
    x_user_id: str,
) -> Response[Union[HTTPValidationError, StatusRequest]]:
    """Метод сохраняет пользовательские данные

    Args:
        x_user_id (str):
        json_body (CreateAuthData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StatusRequest]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
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
    json_body: CreateAuthData,
    x_user_id: str,
) -> Optional[Union[HTTPValidationError, StatusRequest]]:
    """Метод сохраняет пользовательские данные

    Args:
        x_user_id (str):
        json_body (CreateAuthData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StatusRequest]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
        x_user_id=x_user_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: CreateAuthData,
    x_user_id: str,
) -> Response[Union[HTTPValidationError, StatusRequest]]:
    """Метод сохраняет пользовательские данные

    Args:
        x_user_id (str):
        json_body (CreateAuthData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, StatusRequest]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        x_user_id=x_user_id,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Client,
    json_body: CreateAuthData,
    x_user_id: str,
) -> Optional[Union[HTTPValidationError, StatusRequest]]:
    """Метод сохраняет пользовательские данные

    Args:
        x_user_id (str):
        json_body (CreateAuthData):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, StatusRequest]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            x_user_id=x_user_id,
        )
    ).parsed
