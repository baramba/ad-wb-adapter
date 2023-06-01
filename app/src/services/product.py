import asyncio
import uuid

from fastapi import Depends

from adapters.token import TokenManager
from adapters.wb.unofficial.product import ProductAdapter
from depends.adapters.token import get_token_manager
from depends.adapters.unofficial.product import get_product_adapter_un
from dto.unofficial.product import CategoriesDTO, ProductsSubjectDTO
from exceptions.base import WBAErrorNotAuth


class ProductService:
    def __init__(
        self,
        product_adapter: ProductAdapter,
        token_manager: TokenManager,
    ) -> None:
        self.product_adapter = product_adapter
        self.token_manager = token_manager

    async def products(self, user_id: uuid.UUID, subject_id: int) -> ProductsSubjectDTO:
        auth_data = await self.token_manager.auth_data_by_user_id(user_id)
        self.product_adapter.auth_data = auth_data
        try:
            products: ProductsSubjectDTO = await self.product_adapter.products_by_subject(subject_id=subject_id)
            return products
        except WBAErrorNotAuth:
            await self.token_manager.request_update_user_access_token(
                user_id=user_id,
                wb_token_access=auth_data.wb_token_access,
            )
            await asyncio.sleep(2)
            self.product_adapter.auth_data = await self.token_manager.auth_data_by_user_id(user_id)
        products = await self.product_adapter.products_by_subject(subject_id=subject_id)
        return products

    async def categories(self, user_id: uuid.UUID) -> CategoriesDTO:
        auth_data = await self.token_manager.auth_data_by_user_id(user_id)
        self.product_adapter.auth_data = auth_data
        try:
            categories: CategoriesDTO = await self.product_adapter.categories()
            return categories
        except WBAErrorNotAuth:
            # await self.token_manager.request_update_user_access_token(
            #     user_id=user_id,
            #     wb_token_access=auth_data.wb_token_access,
            # )
            await asyncio.sleep(3)
            auth_data = await self.token_manager.auth_data_by_user_id(user_id)
            self.product_adapter.auth_data = auth_data
        categories = await self.product_adapter.categories()
        return categories


async def get_product_service(
    product_adapter: ProductAdapter = Depends(get_product_adapter_un),
    token_manager: TokenManager = Depends(get_token_manager),
) -> ProductService:
    return ProductService(
        product_adapter=product_adapter,
        token_manager=token_manager,
    )
