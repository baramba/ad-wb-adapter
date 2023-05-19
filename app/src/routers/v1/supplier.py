import traceback
from core.settings import logger
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse
from exceptions.base import WBAError
from schemas.v1.base import BaseResponse, BaseResponseError
from schemas.v1.supplier import (
    WBToken,
    WBTokenRequest,
    WBTokenResponse,
)
from services.supplier import SupplierService, get_supplier_service

router = APIRouter(prefix="/suppliers", tags=["supplier"])


@router.post(
    path="/token",
    description="Обменивает refresh wb_token на access wb_token.",
    summary="Возвращает access wb_token пользователя.",
    responses={
        status.HTTP_200_OK: {"model": WBTokenResponse},
    },
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
        logger.error(f"{e}\n{traceback.format_exc()}")
        return ORJSONResponse(
            content=BaseResponseError(
                description="Ошибка при получении авторизационных данных."
            ).dict()
        )
    return ORJSONResponse(
        content=WBTokenResponse(payload=WBToken(wb_token_access=wb_token_access)).dict()
    )
