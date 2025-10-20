# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from db import insert_item, get_items, mark_items_paid

# ================== Models ==================
class CartItemIn(BaseModel):
    name: str
    price: float

class CartItemOut(CartItemIn):
    id: str
    paid: bool = False

class CheckoutItem(BaseModel):
    name: str
    price: float

class CartCheckoutIn(BaseModel):
    items: List[CheckoutItem]
    payment_method: str  # e.g., "UPI", "Card"
    upi_id: Optional[str] = None  # required if payment_method is UPI/GPay

class CheckoutResponse(BaseModel):
    status: str
    amount_paid: float
    transaction_id: Optional[str] = None
    message: str

# ================== App ==================
app = FastAPI(title="RetailX Backend with UPI Checkout")

# ================== Root Endpoint ==================
@app.get("/")
def root():
    return {"message": "RetailX Backend is running"}

# ================== Add Item Endpoint ==================
@app.post("/add_item", response_model=CartItemOut)
def add_item(item: CartItemIn):
    try:
        doc_id = insert_item(item.name, float(item.price))
        if not doc_id:
            raise HTTPException(status_code=500, detail="Failed to insert item into DB")
        return {"id": str(doc_id), "name": item.name, "price": item.price, "paid": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== List Items Endpoint ==================
@app.get("/items", response_model=List[CartItemOut])
def list_items(limit: int = 50):
    try:
        items = get_items(limit=limit)
        result = []
        for it in items:
            result.append({
                "id": str(it.get("_id", "")),
                "name": it.get("name", ""),
                "price": float(it.get("price", 0.0)),
                "paid": it.get("paid", False)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== Checkout Endpoint ==================
@app.post("/checkout", response_model=CheckoutResponse)
def checkout(cart: CartCheckoutIn):
    try:
        # Validate UPI info if GPay/UPI is chosen
        if cart.payment_method.lower() in ["upi", "gpay"] and not cart.upi_id:
            raise HTTPException(status_code=400, detail="UPI ID required for UPI/GPay payment")

        # Calculate total from items sent
        total_amount = sum(item.price for item in cart.items)

        # Mark all items in DB as paid (mock)
        mark_items_paid()  # assumes DB marks current cart items as paid

        # Generate mock transaction ID
        transaction_id = str(uuid4())[:8]

        return CheckoutResponse(
            status="success",
            amount_paid=total_amount,
            transaction_id=transaction_id,
            message=f"Payment received via {cart.payment_method.upper()}"
                    + (f" (UPI ID: {cart.upi_id})" if cart.upi_id else "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
