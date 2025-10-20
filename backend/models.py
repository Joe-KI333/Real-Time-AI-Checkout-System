from typing import List
from pydantic import BaseModel

class CartItemIn(BaseModel):
    name: str
    price: float

class CartItemOut(BaseModel):
    id: str
    name: str
    price: float


class CheckoutItem(BaseModel):
    name: str
    price: float

class CartCheckoutIn(BaseModel):
    items: List[CheckoutItem]
