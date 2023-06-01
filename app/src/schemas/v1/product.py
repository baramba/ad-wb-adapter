import datetime

from schemas.common import BaseOrjsonModel
from schemas.v1.base import BaseResponseSuccess


class MediaFile(BaseOrjsonModel):
    value: str
    thumbnail: str
    mimeType: str


class Product(BaseOrjsonModel):
    imtID: int
    nmID: int
    vendorCode: int
    updateAt: datetime.datetime
    title: str
    mediaFiles: list[MediaFile]
    brandName: str
    subjectName: str
    colorNames: list[str]
    rating: float
    productRating: str
    tags: list[str]
    totalStock: int
    basketCountDown: int


class Products(BaseOrjsonModel):
    products: list[Product]


class ProductResponse(BaseResponseSuccess):
    payload: Products


class Category(BaseOrjsonModel):
    id: int
    name: str


class Categories(BaseOrjsonModel):
    categories: list[Category]


class CategoryResponse(BaseResponseSuccess):
    payload: Categories | None


class ProductSubject(BaseOrjsonModel):
    nm: int
    name: str


class ProductsSubject(BaseOrjsonModel):
    products: list[ProductSubject] | None


class ProductSubjectResponse(BaseResponseSuccess):
    payload: ProductsSubject | None
