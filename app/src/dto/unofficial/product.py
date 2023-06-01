import datetime

from pydantic import Field

from schemas.common import BaseOrjsonModel


class MediaFileDTO(BaseOrjsonModel):
    value: str
    thumbnail: str
    mimeType: str


class MediaFilesDTO(BaseOrjsonModel):
    mediaFiles: dict[str, MediaFileDTO]


class ProductDTO(BaseOrjsonModel):
    imtID: int
    nmID: int
    vendorCode: int
    updateAt: datetime.datetime
    title: str
    mediaFiles: MediaFilesDTO
    brandName: str
    subjectName: str
    colorNames: list[str]
    rating: float
    productRating: str
    tags: list[str]
    totalStock: int
    basketCountDown: int


class ProductsDTO(BaseOrjsonModel):
    products: list[ProductDTO]


class Sort(BaseOrjsonModel):
    searchValue: str = ""
    sortColumn: str = "updateAt"
    ascending: bool = False


class Filter(BaseOrjsonModel):
    tags: dict = Field(default_factory=list)
    brands: dict = Field(default_factory=list)
    subjects: dict = Field(default_factory=list)
    count: int = 0


class Cursor(BaseOrjsonModel):
    n: int = 100


class ProductRequestBodyDTO(BaseOrjsonModel):
    sort: Sort = Sort()
    filter: Filter = Filter()
    cursor: Cursor = Cursor()


class CategoryDTO(BaseOrjsonModel):
    id: int
    name: str


class CategoriesDTO(BaseOrjsonModel):
    categories: list[CategoryDTO]


class ProductSubjectDTO(BaseOrjsonModel):
    nm: int
    name: str


class ProductsSubjectDTO(BaseOrjsonModel):
    products: list[ProductSubjectDTO] | None
