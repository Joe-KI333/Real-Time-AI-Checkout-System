# Real Time AI Checkout System YOLOv11 + FastAPI + MongoDB Integration
<img width="1280" height="720" alt="Building a Real-Time AI Checkout System  YOLOv8 + FastAPI + MongoDB Integration" src="https://github.com/user-attachments/assets/28e5afac-9245-4e90-bd55-ff65ec20d395" />

## 📺 YouTube Demo

For a better understanding, check out the YouTube demo here 👉🏿 [DEMO VIDEO](https://youtu.be/jVxcgLO67Y8?si=y9imMCMyOUoYjxac)
## What is included.
- detection/ : YOLOV11 + OpenCV demo that detects items and maintains a cart overlay.
- backend/ : FastAPI server that receives detected items and stores them in MongoDB.
- docs/payments_security.md : conceptual write-up for payments & security.
- model/* : place your YOLOV11 weights and classes.txt here.
- sample_data/ : sample images.

## Setup (PC)
1. Create venv & install:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run backend:
   - Ensure MongoDB is running (local or set MONGO_URI).
   - Start FastAPI:
     ```bash
     cd backend
     uvicorn main:app --reload --host 0.0.0.0 --port 8000
     ```
3. Run detection:
   - Place weights in `model/YOLOV11n.pt` or edit env var YOLO_WEIGHTS.
   - From repo root:
     ```bash
     cd detection
     python app_detection.py --source 0
     ```
   - Press `q` to quit. Press `r` to reset cart counts.
