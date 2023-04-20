import traceback
from core.settings import logger
from fastapi import APIRouter, Depends, HTTPException, status
from exceptions.base import WBAError
from schemas.v1.base import ResponseCode
from schemas.v1.supplier import (
    WBToken,
    WBTokenErrorResponse,
    WBTokenRequest,
    WBTokenSuccessResponse,
)
from services.supplier import SupplierService, get_supplier_service

router = APIRouter(prefix="/suppliers", tags=["supplier"])


@router.post(
    path="/token",
    description="Обменивает refresh wb_token на access wb_token.",
    summary="Возвращает access wb_token пользователя.",
    responses={
        status.HTTP_200_OK: {"model": WBTokenSuccessResponse},
    },
)
async def auth_wb_user(
    body: WBTokenRequest,
    supplier_service: SupplierService = Depends(get_supplier_service),
) -> WBTokenSuccessResponse:
    try:
        wb_token_access = await supplier_service.get_auth_wb_user(
            wb_token_refresh=body.wb_token_refresh,
            wb_x_supplier_id_external=body.wb_supplier_id,
        )
    except WBAError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=WBTokenErrorResponse(
                status_code=e.status_code,
                description=e.description,
            ).dict(),
        )
    except Exception as e:
        logger.error(f"{e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=WBTokenErrorResponse(
                status_code=ResponseCode.ERROR,
                description="Ошибка при получении wb_token_access.",
            ).dict(),
        )
    return WBTokenSuccessResponse(body=WBToken(wb_token=wb_token_access))
