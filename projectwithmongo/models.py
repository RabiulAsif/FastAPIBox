from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Product(BaseModel):
      id: Optional[str] = Field(alias="_id")
      name: str
      description: str
      price: float
      quantity: int
      
class User(BaseModel):
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        populate_by_name = True 