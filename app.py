"""
SecureScan AI — Flask Application
AI-Powered X-Ray Baggage Security Detection System
Uses YOLOv8 (best.pt) for inference on uploaded X-ray images.
"""

import os
import sys
import time
import json
import uuid
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, send_file, flash, abort
)
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB

UPLOAD_FOLDER = os.path.join("static", "uploads")
RESULT_FOLDER = os.path.join("static", "results")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Threat class names (lowercase for matching)
THREAT_CLASSES = [
    "knife", "gun", "pistol", "firearm", "explosive", "bomb",
    "grenade", "weapon", "rifle", "blade", "scissors", "razor",
    "bullet", "ammunition", "detonator", "handgun", "revolver",
    "sword", "axe", "taser", "brass knuckles",
]

# Colour palette for bounding boxes
COLOR_THREAT = (71, 68, 239)    # #EF4444 in BGR
COLOR_SAFE   = (94, 197, 34)    # #22C55E in BGR
COLOR_TEXT_BG_THREAT = (71, 68, 239)
COLOR_TEXT_BG_SAFE   = (94, 197, 34)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ──────────────────────────────────────────────
# Model Loading
# ──────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best.pt")

if not os.path.isfile(MODEL_PATH):
    print("\n" + "=" * 60)
    print("  ERROR: best.pt not found!")
    print(f"  Expected location: {MODEL_PATH}")
    print("  Please place your trained YOLOv8 model (best.pt) in the")
    print("  project root directory and restart the application.")
    print("=" * 60 + "\n")
    sys.exit(1)

print("[SecureScan AI] Loading YOLOv8 model …")
model = YOLO(MODEL_PATH)
print("[SecureScan AI] Model loaded successfully ✓")


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_threat_class(class_name: str) -> bool:
    """Check whether a detected class is considered a threat."""
    name_lower = class_name.lower().strip()
    for threat in THREAT_CLASSES:
        if threat in name_lower or name_lower in threat:
            return True
    return False


def draw_detections(image_bgr: np.ndarray, detections: list) -> np.ndarray:
    """Draw bounding boxes and labels on the image."""
    annotated = image_bgr.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 2

    for det in detections:
        x1, y1, x2, y2 = [int(c) for c in det["box"]]
        label = f'{det["class"]} {det["confidence"]:.0%}'
        color = COLOR_THREAT if det["is_threat"] else COLOR_SAFE
        text_bg = COLOR_TEXT_BG_THREAT if det["is_threat"] else COLOR_TEXT_BG_SAFE

        # Bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)

        # Label background
        (tw, th), baseline = cv2.getTextSize(label, font, font_scale, 1)
        label_y = max(y1 - 6, th + 6)
        cv2.rectangle(
            annotated,
            (x1, label_y - th - 6),
            (x1 + tw + 8, label_y + 4),
            text_bg, -1,
        )
        cv2.putText(
            annotated, label,
            (x1 + 4, label_y - 2),
            font, font_scale, (255, 255, 255), 1, cv2.LINE_AA,
        )

    return annotated


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@app.route("/scan")
def scan():
    """Upload page."""
    return render_template("scan.html")


@app.route("/predict", methods=["POST"])
def predict():
    """Handle image upload, run YOLO inference, redirect to results."""
    # --- Validate ---
    if "image" not in request.files:
        flash("No file uploaded. Please select an image.", "error")
        return redirect(url_for("scan"))

    file = request.files["image"]
    if file.filename == "":
        flash("No file selected. Please choose an image.", "error")
        return redirect(url_for("scan"))

    if not allowed_file(file.filename):
        flash("Invalid file type. Allowed: JPG, JPEG, PNG.", "error")
        return redirect(url_for("scan"))

    try:
        # --- Save uploaded image ---
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(upload_path)

        # --- Image metadata ---
        pil_img = Image.open(upload_path)
        img_width, img_height = pil_img.size
        pil_img.close()

        # --- YOLO inference ---
        start_time = time.time()
        results = model(upload_path, conf=0.25)
        processing_ms = round((time.time() - start_time) * 1000, 1)

        # --- Parse detections ---
        detections = []
        result = results[0]
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            detections.append({
                "class": class_name,
                "confidence": confidence,
                "is_threat": is_threat_class(class_name),
                "box": xyxy,
            })

        # Sort by confidence descending
        detections.sort(key=lambda d: d["confidence"], reverse=True)

        # --- Draw bounding boxes ---
        image_bgr = cv2.imread(upload_path)
        annotated = draw_detections(image_bgr, detections)
        result_path = os.path.join(RESULT_FOLDER, unique_name)
        cv2.imwrite(result_path, annotated)

        # --- Verdict ---
        is_safe = not any(d["is_threat"] for d in detections)

        # --- Store in session ---
        session["result_data"] = {
            "result_image": f"results/{unique_name}",
            "original_image": f"uploads/{unique_name}",
            "detections": detections,
            "is_safe": is_safe,
            "count": len(detections),
            "processing_ms": processing_ms,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "width": img_width,
            "height": img_height,
            "filename": unique_name,
        }

        return redirect(url_for("result"))

    except Exception as exc:
        print(f"[SecureScan AI] Error during prediction: {exc}")
        flash(f"Something went wrong during analysis: {str(exc)}", "error")
        return redirect(url_for("scan"))


@app.route("/result")
def result():
    """Display detection results."""
    data = session.get("result_data")
    if not data:
        flash("No scan results available. Please upload an image first.", "error")
        return redirect(url_for("scan"))
    return render_template("result.html", data=data)


@app.route("/download/<filename>")
def download(filename):
    """Download the annotated result image."""
    safe_name = secure_filename(filename)
    file_path = os.path.join(RESULT_FOLDER, safe_name)
    if not os.path.isfile(file_path):
        abort(404)
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"securescan_result_{safe_name}",
    )


# ──────────────────────────────────────────────
# Error handlers
# ──────────────────────────────────────────────
@app.errorhandler(413)
def file_too_large(e):
    flash("File is too large. Maximum size is 10 MB.", "error")
    return redirect(url_for("scan"))


@app.errorhandler(404)
def not_found(e):
    return render_template("base.html", error_404=True), 404


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  SecureScan AI — Running on http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
