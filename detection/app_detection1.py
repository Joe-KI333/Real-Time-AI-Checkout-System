"""
Retail - CV Checkout with UPI/GPay Mock Payment
"""

import cv2
import json
import argparse
import requests
import os
import numpy as np
from ultralytics import YOLO

# ================== CONFIG ==================
CONF_THRESHOLD = 0.30
OVERLAY_WIDTH_RATIO = 0.28

MODEL_PATH = os.getenv("YOLO_WEIGHTS", "../model/YOLO11n.pt")
CLASSES_FILE = os.getenv("CLASSES_FILE", "../model/classes.txt")
PRICES_FILE = "sample_prices.json"
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
CHECKOUT_URL = f"{BACKEND_URL}/checkout"
ADD_ITEM_URL = f"{BACKEND_URL}/add_item"

# ================== ROI ==================
BASE_POLYGON = np.array([
    [100, 200],
    [540, 200],
    [600, 470],
    [40, 470]
], np.int32)

# ================== Price Map ==================
if os.path.exists(PRICES_FILE):
    with open(PRICES_FILE, "r") as f:
        PRICE_MAP = json.load(f)
else:
    PRICE_MAP = {}

# ================== Class Names ==================
if os.path.exists(CLASSES_FILE):
    with open(CLASSES_FILE, "r") as f:
        CLASS_NAMES = [line.strip() for line in f.readlines() if line.strip()]
else:
    CLASS_NAMES = None

# ================== Cart Class ==================
class Cart:
    def __init__(self):
        self.items = {}
        self.transaction_msg = ""

    def add(self, name):
        self.items[name] = self.items.get(name, 0) + 1

    def contains(self, name):
        return name in self.items

    def reset(self):
        self.items = {}
        self.transaction_msg = ""

    def total_amount(self):
        return sum(PRICE_MAP.get(name, 0.0) * count for name, count in self.items.items())

    def to_list(self):
        return [{"name": name, "price": PRICE_MAP.get(name, 0.0)} for name in self.items]

# ================== Drawing Functions ==================
def draw_cart_overlay(frame, cart: Cart):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    overlay_width = int(w * OVERLAY_WIDTH_RATIO)
    cv2.rectangle(overlay, (w - overlay_width, 0), (w, h), (255, 255, 255), -1)
    cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

    x = w - overlay_width + 20
    y = 40

    # Header
    cv2.putText(frame, "CART SUMMARY", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (10, 10, 10), 2)
    y += 40

    # Items
    for name, count in cart.items.items():
        line = f"{name} x{count}"
        total = f"= Rs{PRICE_MAP.get(name, 0.0) * count:.2f}"
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 2)
        cv2.putText(frame, total, (x + 150, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 120), 2)
        y += 28

    y += 20
    cv2.putText(frame, f"TOTAL: Rs{cart.total_amount():.2f}", (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 200), 3)

    # Transaction message
    if cart.transaction_msg:
        y += 40
        cv2.putText(frame, f"{cart.transaction_msg}", (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 120, 0), 2)

# ================== Backend Functions ==================
def post_item_to_backend(item_name, unit_price):
    payload = {"name": item_name, "price": float(unit_price)}
    try:
        r = requests.post(ADD_ITEM_URL, json=payload, timeout=0.6)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

def checkout_cart(cart: Cart, payment_method="UPI", upi_id="user@upi"):
    payload = {
        "payment_method": payment_method,
        "upi_id": upi_id,
        "amount": cart.total_amount(),
        "items": cart.to_list()
    }
    try:
        r = requests.post(CHECKOUT_URL, json=payload, timeout=1.0)
        if r.status_code == 200:
            data = r.json()
            cart.transaction_msg = f"{data.get('status', '')} - TxID: {data.get('transaction_id','')}"
        else:
            cart.transaction_msg = f"Checkout failed ({r.status_code})"
    except Exception as e:
        cart.transaction_msg = f"Checkout error: {str(e)}"

# ================== Detection Logic ==================
def is_inside_cart(x1, y1, x2, y2, polygon):
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    return cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0

def process_frame(frame, model, cart, polygon, send_api=True):
    cv2.polylines(frame, [polygon], isClosed=True, color=(180, 50, 250), thickness=2)
    results = model(frame, stream=False, device="cpu", conf=CONF_THRESHOLD)

    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if not is_inside_cart(x1, y1, x2, y2, polygon):
                continue

            cls_idx = int(box.cls[0])
            name = model.names.get(cls_idx, str(cls_idx))
            conf = float(box.conf[0])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 0), 2)
            cv2.putText(frame, f"{name} ({conf:.2f})", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 0), 2)

            if not cart.contains(name):
                cart.add(name)
                if send_api:
                    post_item_to_backend(name, PRICE_MAP.get(name, 0.0))

    draw_cart_overlay(frame, cart)
    return frame

# ================== Main ==================
def main(source=0, model_path=MODEL_PATH, send_api=True):
    model = YOLO(model_path)
    if CLASS_NAMES:
        model.names = {i: name for i, name in enumerate(CLASS_NAMES)}
    cart = Cart()

    cap = cv2.VideoCapture(int(source) if str(source).isdigit() else source)
    if not cap.isOpened():
        print("Failed to open source:", source)
        return

    ret, frame = cap.read()
    if not ret:
        print("Failed to read first frame.")
        return
    h, w = frame.shape[:2]

    scale_x, scale_y = w / 640.0, h / 480.0
    cart_polygon = np.array([[int(x * scale_x), int(y * scale_y)] for x, y in BASE_POLYGON], np.int32)

    cv2.namedWindow("Retail - CV Checkout", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Retail - CV Checkout", w, h)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = process_frame(frame, model, cart, cart_polygon, send_api)
        cv2.imshow("Retail - CV Checkout", frame)
        k = cv2.waitKey(1) & 0xFF

        if k == ord("q"):
            break
        elif k == ord("r"):
            cart.reset()
        elif k == ord("p"):  # Trigger mock payment
            checkout_cart(cart)

    cap.release()
    cv2.destroyAllWindows()

# ================== Entry Point ==================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=0, help="camera index, video path, or image path")
    parser.add_argument("--model", default=MODEL_PATH, help="YOLO weights path")
    parser.add_argument("--no-api", action="store_true", help="don't POST detections to backend")
    args = parser.parse_args()

    main(source=args.source, model_path=args.model, send_api=not args.no_api)
