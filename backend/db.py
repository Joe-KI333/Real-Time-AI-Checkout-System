# db.py
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["Retailx"]
collection = db["cart_items"]

def insert_item(name: str, price: float):
    doc = {"name": name, "price": price, "paid": False}
    result = collection.insert_one(doc)
    return result.inserted_id
def mark_items_paid():
    """Mark all unpaid cart items as paid."""
    collection.update_many({"paid": {"$ne": True}}, {"$set": {"paid": True}})


def get_items(limit: int = 50):
    return list(collection.find().sort("_id", -1).limit(limit))
