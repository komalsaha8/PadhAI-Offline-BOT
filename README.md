Live Demo: https://padhai-offline-bot-9ih4wkikgcsv3uwafcjr5s.streamlit.app
# PadhAI BOT - Offline Board-to-Notes AI

> No WiFi. No Data Cost. No Privacy Leak. 100% Offline AI on Snapdragon X Elite.

### The Problem
* Students capture RR blackboard photos but never convert them into notes.
* Cloud AI tools like ChatGPT require stable internet, consume mobile data, and leak classroom data.
* In Tier 2/3 cities and rural colleges, classroom internet connectivity is unreliable or zero.

### Our Solution - 3 Step BOT (Board-to-Notes)
An offline AI assistant that runs 100% on-device.

**Step 1: Photo -> Text**
Converts skewed, blurry, and low-light board images into clean digital text. 
*Model: YOLOv8 OCR INT8 (Optimized for NPU) from Qualcomm AI Hub*

**Step 2: Text -> Smart Notes**
Automatically generates concise notes, a quick summary, and 3 practice MCQs from the extracted text.
*Model: Phi-3.5 Mini Instruct (INT4) from Qualcomm AI Hub*

**Step 3: BOT Chat - Offline Doubt Solving**
Students can ask "Explain this in Hindi" or "Test me" and get instant answers without internet.

### Why Snapdragon X Elite?
* **45 TOPS Hexagon NPU:** Efficiently runs INT8/INT4 quantized models.
* **<1W Power Consumption:** Enables 26+ hours battery life for all-day classroom use.
* **100% On-Device AI:** No data leaves the device. Complete privacy and zero internet cost.

### Tech Stack
Qualcomm AI Hub, YOLOv8-OCR-INT8, Phi-3.5 Mini Instruct, Python, Streamlit, ONNX Runtime with QNN Execution Provider

### Target Impact
Built for 10 Crore+ students in Tier 2/3 India who need affordable, offline, and private learning tools.

### Team
Komal Saha - PadhAI BOT
