from pydantic import BaseModel, Field


class CategoryAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class Category(CategoryAdd):
    id: int
