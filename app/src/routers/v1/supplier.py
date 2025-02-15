import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse

from core.settings import logger
from exceptions.base import WBAError
from routers.utils import x_user_id
from schemas.v1.base import BaseResponse, BaseResponseError
from schemas.v1.supplier import Balance, BalanceResponse, WBToken, WBTokenRequest, WBTokenResponse
from services.supplier import SupplierService, get_supplier_service

router = APIRouter(prefix="/suppliers", tags=["supplier"])


@router.post(
    path="/token",
    responses={
        status.HTTP_200_OK: {"model": WBTokenResponse},
    },
    summary="Возвращает access wb_token пользователя.",
    description="Обменивает refresh wb_token на access wb_token.",
)
async def auth_wb_user(
    body: WBTokenRequest,
    supplier_service: SupplierService = Depends(get_supplier_service),
) -> Response:
    try:
        wb_token_access = await supplier_service.get_auth_wb_user(
            wb_token_refresh=body.wb_token_refresh,
            wb_x_supplier_id_external=body.wb_supplier_id,
        )
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(description="Ошибка при получении авторизационных данных.").dict()
        )
    return ORJSONResponse(content=WBTokenResponse(payload=WBToken(wb_token_access=wb_token_access)).dict())


@router.post(
    path="/balance",
    responses={
        status.HTTP_200_OK: {"model": BalanceResponse},
    },
    summary="Возвращает баланс пользователя.",
    description="""Метод для получения баланса пользователя.",
[https://advert-api.wb.ru/adv/v1/balance]\
(https://advert-api.wb.ru/adv/v1/balance)
""",
)
async def balance(
    user_id: Annotated[uuid.UUID, Depends(x_user_id)],
    supplier_service: SupplierService = Depends(get_supplier_service),
) -> Response:
    try:
        balance = await supplier_service.balance()
        return ORJSONResponse(
            content=BalanceResponse(
                payload=Balance(account=balance.balance, balance=balance.net, bonus=balance.bonus)
            ).dict()
        )
    except WBAError as e:
        return ORJSONResponse(content=BaseResponse.parse_obj(e.__dict__).dict())
    except Exception as e:
        logger.exception(e)
        return ORJSONResponse(
            content=BaseResponseError(description="Ошибка при получении баланса пользователя.").dict()
        )
