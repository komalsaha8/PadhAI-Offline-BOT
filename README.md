# PadhAI-Offline-BOT
Offline AI study buddy for Snapdragon HP PCs - Board photo to notes , 100% offline using Qualcomm AI Hub - NO Wifi , No Data Cost, No Privacy Leak.
### The Problem
- Students click blurry board photos but never convert to notes
- Cloud AI (ChatGPT) needs internet, costs data, leaks data
- Tier 2/3 cities me class me internet nahi milta

### Our Solution - 3 Step BOT
**Step 1: Photo -> Text** - Board ka teda-medha photo bhi saaf text me (YOLOv8 OCR INT8 model from Qualcomm AI Hub)
**Step 2: Text -> Smart Notes** - To-the-point notes + summary + 3 MCQs (Phi-3 Mini from Qualcomm AI Hub)
**Step 3: BOT Chat** - "Iska matlab Hindi me samjhao", "Test lo" - sab offline jawab

### Why Snapdragon X Elite?
- 45 TOPS Hexagon NPU pe INT8 models run hote hain
- <1W power -> 26 hours battery
- 100% On-Device AI -> No internet needed

### Tech Stack
Qualcomm AI Hub, YOLOv8-OCR-INT8, Phi-3.5 Mini Instruct, Python, Streamlit, ONNX Runtime with QNN

### Team
Komal Saha - PadhAI BOT
