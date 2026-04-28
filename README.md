# 🛡️ SecureScan AI — AI-Powered X-Ray Baggage Security Detection

SecureScan AI is a web application that uses a custom-trained **YOLOv8** model to detect prohibited items in X-ray baggage scan images. Upload an image, and the system draws bounding boxes around detected objects, displays confidence scores, and provides a clear **SAFE ✅** or **THREAT DETECTED 🚨** verdict.

---

## 📋 Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.10 or higher |
| pip         | Latest recommended |
| Git         | Optional (for cloning) |

### Check your Python version

```bash
python --version
```

If you see `Python 3.10.x` or higher, you're good to go.

---

## 🚀 Setup Guide (Step by Step)

### 1. Clone or Download the Project

```bash
# If using Git:
git clone <your-repo-url>
cd SecureScanAI

# Or simply download and extract the ZIP, then open a terminal in the SecureScanAI folder.
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, Ultralytics (YOLOv8), OpenCV, Pillow, and other required packages.

### 4. Place Your YOLO Model

Copy your trained YOLOv8 model file (`best.pt`) into the **project root directory**:

```
SecureScanAI/
├── app.py
├── best.pt    ← Place your model HERE
├── ...
```

> ⚠️ The application will **not start** without `best.pt`. Make sure the file is named exactly `best.pt`.

### 5. Run the Application

```bash
python app.py
```

You should see output like:

```
[SecureScan AI] Loading YOLOv8 model …
[SecureScan AI] Model loaded successfully ✓

==================================================
  SecureScan AI — Running on http://127.0.0.1:5000
==================================================
```

### 6. Open in Browser

Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

---

## 🖥️ Using the Application

1. **Landing Page** — Click **"Start Scanning →"** to go to the upload page.
2. **Upload Page** — Drag & drop an X-ray image or click to browse. Supported formats: JPG, PNG, JPEG (max 10 MB).
3. **Results Page** — View the annotated image with bounding boxes, detected items with confidence scores, and the safety verdict.

---

## 📁 Project Structure

```
SecureScanAI/
├── app.py                    ← Flask application (main entry point)
├── best.pt                   ← Your trained YOLOv8 model
├── requirements.txt          ← Python dependencies
├── static/
│   ├── css/
│   │   └── style.css         ← All styles
│   ├── js/
│   │   └── main.js           ← Upload interaction, drag-and-drop, loader
│   ├── images/
│   │   └── logo.svg          ← Shield/scan logo
│   ├── uploads/              ← Uploaded images (auto-created)
│   └── results/              ← Annotated result images (auto-created)
├── templates/
│   ├── base.html             ← Base template with navbar + footer
│   ├── index.html            ← Landing page
│   ├── scan.html             ← Upload page
│   └── result.html           ← Results page
└── README.md                 ← This file
```

---

## ❗ Common Errors & Solutions

| Error | Solution |
|-------|----------|
| `ERROR: best.pt not found!` | Place your `best.pt` model file in the project root directory. |
| `ModuleNotFoundError: No module named 'flask'` | Activate your virtual environment and run `pip install -r requirements.txt`. |
| `ModuleNotFoundError: No module named 'ultralytics'` | Run `pip install ultralytics`. |
| `File is too large` | Reduce the image size to under 10 MB. |
| `Invalid file type` | Only JPG, JPEG, and PNG files are accepted. |
| Port 5000 already in use | Change the port in `app.py`: `app.run(port=5001)`. |

---

## 🧪 Tech Stack

- **Backend:** Python 3.10+, Flask
- **AI Model:** Ultralytics YOLOv8
- **Image Processing:** OpenCV, Pillow
- **Frontend:** HTML5, CSS3, Vanilla JavaScript

---

## 📄 License

This project is for **demonstration and research purposes only**. Use responsibly.

---

**SecureScan AI © 2025 — Powered by YOLOv8 + Flask**
