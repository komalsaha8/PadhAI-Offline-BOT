## Live Demo

**[https://padhai-offline-bot-9ih4wkikgcsv3uwafcjr5s.streamlit.app](https://padhai-offline-bot-9ih4wkikgcsv3uwafcjr5s.streamlit.app)**

> Note: This link is a cloud-hosted demo, provided only so judges can try the pipeline instantly without installing anything. It requires internet to load, same as any demo video or hosted preview would.
> The actual product is designed to run as a locally installed application directly on a Snapdragon-powered HP PC. Once installed, it needs no internet connection at all - OCR, notes generation, and chat all run fully on-device using the Hexagon NPU. This demo link is a convenience for evaluation, not a representation of how the final offline product will be accessed.

---

# PadhAI BOT - Offline Board-to-Notes AI

> No WiFi. No Data Cost. No Privacy Leak. Designed to be optimized for Snapdragon-powered HP PCs.

**Submission:** Snapdragon AI Lab Build & Present Challenge
**Status:** Working CPU prototype (this repo) - proposed to be rebuilt on Qualcomm AI Hub models for on-device deployment on Snapdragon-powered HP PCs.

---

## The Problem

- Students capture blurry blackboard photos but rarely convert them into usable notes.
- Cloud AI tools like ChatGPT need stable internet, consume mobile data, and raise privacy concerns around classroom content.
- In Tier 2/3 cities and rural colleges, classroom internet connectivity is unreliable or completely absent.

---

## Our Solution - 3-Step BOT (Board-to-Notes)

An AI assistant designed to run 100% on-device, with no cloud dependency at any step.

### Step 1: Photo to Text
Converts board images into clean digital text.

### Step 2: Text to Smart Notes
Automatically generates a summary, structured notes, and practice MCQs from the extracted text.

### Step 3: BOT Chat - Doubt Solving
Students can ask things like "Explain this in Hindi" or "Test me" and get instant answers.

---

## Current Status - What's Working vs What's Proposed

This repo contains a **working, runnable prototype** so judges can see the full pipeline in action, not just a concept. It intentionally uses lightweight, free, CPU-only components so it runs anywhere without Snapdragon hardware. The AI model layer is designed to be swapped for Qualcomm AI Hub models for the final on-device build.

| Stage | This Prototype (CPU, works today) | Proposed Final Build (Snapdragon-powered HP PC) |
|---|---|---|
| OCR | Tesseract OCR | **YOLOv8-OCR (INT8)** - Qualcomm AI Hub, on Hexagon NPU |
| Notes / Summary / MCQ | Rule-based generator (extractive summary + fill-in-the-blank MCQs) | **Phi-3.5 Mini Instruct (INT4)** - Qualcomm AI Hub, on Hexagon NPU |
| Chat / Doubt Solving | Template-based demo responses | Phi-3.5 Mini Instruct, fully on-device, real multilingual Q&A |
| Inference Runtime | Python / CPU | ONNX Runtime with QNN Execution Provider |
| Target Hardware | Any machine (demo) | Snapdragon-powered HP PC (Hexagon NPU) |

This approach was chosen deliberately: it proves the **pipeline, UX, and product logic work end-to-end** right now, while clearly separating what still needs to be ported to Qualcomm AI Hub's NPU-optimized models on actual Snapdragon hardware.

---

## Proposed Architecture (Final Build)

```
Board Photo
    |
    v
------------------------
 OCR Module
 (Hexagon NPU)
 Model: YOLOv8-OCR (INT8) - Qualcomm AI Hub
 Function: Handles skew / blur / low-light correction
------------------------
    |  extracted text
    v
------------------------
 Notes Generator
 (Hexagon NPU)
 Model: Phi-3.5 Mini Instruct (INT4) - Qualcomm AI Hub
 Function: Summary + Notes + MCQs
------------------------
    |  structured notes
    v
------------------------
 BOT Chat Interface
 (On-device inference)
 Interface: Streamlit UI
 Function: Doubt-solving, translation, quizzing
------------------------

All processing to run on-device via ONNX Runtime + QNN Execution Provider
on a Snapdragon-powered HP PC - no data will leave the device.
```

---

## Why This Fits Snapdragon-Powered HP PCs

- **Hexagon NPU:** Provides the on-device compute headroom needed to run INT8/INT4 quantized OCR and LLM models locally, without any cloud offload.
- **Power efficiency:** Snapdragon's low-power NPU architecture makes an always-available, all-day classroom tool realistic on an HP PC - exact battery/power benchmarks will be measured once ported to Snapdragon hardware.
- **On-device AI by design:** The final solution is built around quantized models sourced directly from Qualcomm AI Hub, avoiding any network round-trip for OCR or text generation.

---

## How to Run This Prototype Locally

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd padhai-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Tesseract OCR engine
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr
# Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract

# 4. Run the app
streamlit run app.py
```

The app opens in your browser. Upload a board photo (or type text manually) to see OCR to Notes to MCQ to Chat working end-to-end.

### Deploying (for judges to access via a link)
This app is ready to deploy on Streamlit Community Cloud (streamlit.io/cloud) for free:
1. Push this repo to GitHub.
2. On share.streamlit.io, create a new app pointing to `app.py`.
3. Streamlit Cloud auto-installs `packages.txt` (tesseract-ocr) and `requirements.txt`.

---

## Tech Stack

| Component | Prototype (this repo) | Final Proposed Build |
|---|---|---|
| OCR | Tesseract OCR | YOLOv8-OCR (INT8), Qualcomm AI Hub |
| Notes/Chat | Rule-based Python | Phi-3.5 Mini Instruct (INT4), Qualcomm AI Hub |
| Runtime | Python | ONNX Runtime + QNN Execution Provider |
| Interface | Streamlit | Streamlit |
| Target Hardware | Any CPU | Snapdragon-powered HP PC |

---

## Development Roadmap

- [x] **Phase 0 (Done):** Working CPU prototype - OCR, notes/MCQ generation, chat UX, deployed and demoable.
- [ ] **Phase 1:** Replace Tesseract with YOLOv8-OCR (INT8) from Qualcomm AI Hub; benchmark on Snapdragon-powered HP PC.
- [ ] **Phase 2:** Replace rule-based notes/MCQ generator with Phi-3.5 Mini Instruct (INT4) running via ONNX Runtime + QNN Execution Provider.
- [ ] **Phase 3:** Enable real offline multilingual chat (Hindi explanation, quizzing) using the on-device LLM.
- [ ] **Phase 4:** On-device benchmarking (latency, power draw, battery impact) and UI polish for classroom use.

---

## Target Impact

Aimed at 10 Crore+ students across Tier 2/3 India who need affordable, offline, and private learning tools - particularly in classrooms where internet access is unreliable or unavailable.

---

## Team

**Komal Saha** - Idea, design, and build for PadhAI BOT (solo submission).

---

*This repository contains a working prototype demonstrating the proposed PadhAI BOT pipeline. In line with the Snapdragon AI Lab Build & Present Challenge requirements, the final solution is intended to be optimized for Snapdragon-powered HP PCs using AI models from Qualcomm AI Hub.*
