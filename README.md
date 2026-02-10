# JuteVision Auditor

Professional jute audit app: scan, upload images, save, and PIN-protected access.  
**Obsidian & Emerald** theme. Ready for phone (PWA) and desktop.

---

## Run the app

```powershell
.\run_app.ps1
```

- **Desktop:** http://localhost:8000  
- **Phone (same Wi‑Fi):** http://\<PC_IP\>:8000

---

## Features

### Actions
- **Scan** – Start live audit with camera
- **Stop** – End scan (with confirmation)
- **Reset** – Clear session (with confirmation)
- **Upload Image** – Upload image, run YOLO, optionally save
- **Save Image** – Capture current frame and save (with confirmation)

### Safety
- **App PIN** – Lock the app. Enable in Settings.
- **File Access PIN** – Required for Save & Saved Images. Enable in Settings.
- Toggle each PIN on/off in Settings.

### Other
- **Saved Images** – View saved captures (folder icon in header)
- **Settings** – Configure PINs (gear icon in header)
- Confirmation popups for Stop, Reset, Save

---

## Using on phone

### When phone and PC are on the same Wi‑Fi
1. Run `.\run_app.ps1` (or `.\run_streamlit.ps1` for the Control Center) on PC
2. On phone, connect to the **same Wi‑Fi** as the PC
3. Open http://\<PC_IP\>:8000 (or :8501 for Streamlit)
4. Add to Home Screen for app-like icon (PWA)

### When phone is on 4G and PC is on Wi‑Fi (different networks)
The app URL (e.g. `http://192.168.0.185:8501`) is **local only**. Your phone on 4G cannot reach it, so you may see an error or a “login” page.

- **Option A (easiest):** Connect your phone to the **same Wi‑Fi** as the PC when you want to use the dashboard. Then use the Local or Network URL shown in the terminal.
- **Option B (use app over 4G):** Expose the app with a tunnel so the phone can reach it from the internet. Run the Streamlit app, then in another terminal run:  
  `ngrok http 8501`  
  (Install ngrok from https://ngrok.com and sign up for a free account.) Use the `https://….ngrok-free.app` URL on your phone.

---

## Next step

Train a jute-specific model and update `backend/app/camera.py` to use it. The app is ready; only the model needs to be replaced.
run_streamlit.ps1
[theme]
primaryColor = "#50C878"          # Emerald Green for Results
backgroundColor = "#0E1117"       # Dark Industrial Background
secondaryBackgroundColor = "#262730" # Card Background
textColor = "#FFFFFF"             # Main Text is White (Hello Inspector)
font = "sans serif"
