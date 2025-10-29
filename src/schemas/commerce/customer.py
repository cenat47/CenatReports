from pydantic import BaseModel, Field


class CustomerAdd(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    address: str = Field(min_length=1, max_length=200)


class Customer(CustomerAdd):
    id: int
