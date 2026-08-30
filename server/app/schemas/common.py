from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)
    total_items: int = Field(ge=0, default=0)
    total_pages: int = Field(ge=0, default=0)
    has_next: bool = False
    has_prev: bool = False


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
