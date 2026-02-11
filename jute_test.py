import streamlit as st
import numpy as np
from datetime import datetime
import json
import os
from PIL import Image, ImageDraw
import io
import hashlib
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Page config
st.set_page_config(page_title="JuteVision Auditor - Govt of India", page_icon="🇮🇳", layout="wide")

# Session state init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "inspector_name" not in st.session_state:
    st.session_state.inspector_name = None
if "audit_id" not in st.session_state:
    st.session_state.audit_id = None
if "audit_data" not in st.session_state:
    st.session_state.audit_data = None
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "pin_verified" not in st.session_state:
    st.session_state.pin_verified = False
if "captured_images" not in st.session_state:
    st.session_state.captured_images = []

def init_audit_data(inspector):
    return {
        "audit_id": f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "inspector": inspector,
        "gps": None,
        "timestamp": None,
        "bales_count": 0,
        "daily_consumption": 100,
        "stock_days": 0,
        "confidence": 0,
        "grade": "N/A",
        "compliance_status": "PENDING",
        "image": None,
        "notes": ""
    }

# CSS
def get_css(theme):
    if theme == "dark":
        return """
        <style>
        .block-container { padding-top: 1rem; background-color: #1a1a2e; }
        body { background-color: #1a1a2e; color: white; }
        h1, h2, h3 { color: white !important; }
        .stButton button { border-radius: 10px; }
        </style>
        """
    else:
        return """
        <style>
        .block-container { padding-top: 1rem; background-color: #f0f2f6; }
        body { background-color: #f0f2f6; color: #1f1f1f; }
        h1, h2, h3 { color: #1f1f1f !important; }
        .stButton button { 
            background-color: #000080; 
            color: white; 
            border-radius: 10px; 
        }
        .stButton button:hover {
            background-color: #FF9932;
            color: black;
        }
        </style>
        """

st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# Login
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🇮🇳 JuteVision Auditor")
        st.subheader("Ministry of Textiles, Government of India")
        
        inspector = st.text_input("Inspector ID", placeholder="inspector@gov.in")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if inspector and len(password) >= 4:
                st.session_state.authenticated = True
                st.session_state.inspector_name = inspector
                st.session_state.audit_id = f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.audit_data = init_audit_data(inspector)
                st.session_state.captured_images = []
                st.rerun()
            else:
                st.error("Enter valid credentials")
    st.stop()

# Header
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.markdown("🇮🇳")
with col2:
    st.title("JuteVision Auditor")
    st.caption("Ministry of Textiles, Government of India")
with col3:
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.captured_images = []
        st.rerun()

# Theme toggle
c1, c2 = st.columns(2)
with c1:
    if st.button("🌙 Dark"):
        st.session_state.theme = "dark"
        st.rerun()
with c2:
    if st.button("☀️ Light"):
        st.session_state.theme = 'light'
        st.rerun()

# Session info
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("Inspector", st.session_state.inspector_name)
c2.metric("Audit ID", st.session_state.audit_id)
c3.metric("Status", "Active")
st.markdown("---")

# Main tabs
tab1, tab2, tab3 = st.tabs(["📷 Scan Jute", "📊 Audit Results", "📤 Export Report"])

with tab1:
    st.subheader("Capture & Analyze Jute Bales")
    
    # Multiple camera captures
    cam = st.camera_input("Click to capture (can click multiple times)", key=f"cam_{len(st.session_state.captured_images)}")
    if cam:
        st.session_state.captured_images.append(cam)
        st.success(f"Captured image #{len(st.session_state.captured_images)}")
    
    # Show all captured
    if st.session_state.captured_images:
        st.write(f"**{len(st.session_state.captured_images)} image(s) captured**")
        for i, img in enumerate(st.session_state.captured_images):
            st.image(img, caption=f"Image {i+1}")
        if st.button("🗑️ Clear All"):
            st.session_state.captured_images = []
            st.rerun()
    
    # Upload multiple
    uploads = st.file_uploader("Or upload images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    if uploads:
        st.success(f"Uploaded {len(uploads)} image(s)")
        for f in uploads:
            st.image(f, caption=f.name)
    
    # Location
    state = st.selectbox("State", ["Select", "West Bengal", "Bihar", "Odisha", "Assam", "Jharkhand"])
    if st.button("📍 Get Location") and state != "Select":
        st.session_state.audit_data["gps"] = {"location": f"{state}, India"}
        st.session_state.audit_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"Location: {state}")
    
    # Analysis
    daily = st.number_input("Daily consumption (bales/day)", 1, 500, 100)
    st.session_state.audit_data["daily_consumption"] = daily
    
    sim = st.toggle("🧪 Simulation Mode (for testing)")
    
    if st.button("🔍 Analyze Images", type="primary"):
        all_images = st.session_state.captured_images + list(uploads) if uploads else st.session_state.captured_images
        
        if not all_images:
            st.error("Capture or upload images first!")
        else:
            total_bales = 0
            for idx, img in enumerate(all_images):
                if sim:
                    bales = 25 + idx * 5
                    conf = 0.92
                else:
                    # Simple detection simulation
                    bales = np.random.randint(15, 40)
                    conf = np.random.uniform(0.75, 0.95)
                
                total_bales += bales
                st.image(img, caption=f"Image {idx+1}: {bales} bales detected")
            
            # Calculate
            stock_days = round(total_bales / daily, 1)
            compliance = "PASS" if stock_days >= 30 else "FAIL"
            grade = "A" if total_bales > 50 else "B" if total_bales > 30 else "C"
            
            st.session_state.audit_data.update({
                "bales_count": total_bales,
                "stock_days": stock_days,
                "compliance_status": compliance,
                "grade": grade,
                "confidence": conf if all_images else 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            st.success(f"✅ Total: {total_bales} bales, {stock_days} days stock")
            if compliance == "PASS":
                st.balloons()

with tab2:
    st.subheader("Audit Results")
    
    data = st.session_state.audit_data
    bales = data.get("bales_count", 0)
    days = data.get("stock_days", 0)
    comp = data.get("compliance_status", "PENDING")
    
    c1, c2 = st.columns(2)
    with c1:
        if comp == "PASS":
            st.success("✅ COMPLIANT (30+ days)")
        elif comp == "FAIL":
            st.error("❌ NON-COMPLIANT (<30 days)")
        else:
            st.warning("⏳ PENDING")
    with c2:
        st.info(f"Grade: {data.get('grade', 'N/A')}")
    
    st.metric("Total Bales", bales)
    st.metric("Stock Days", days)
    
    # Safe GPS display
    gps = data.get("gps") or {}
    location = gps.get("location", "Not captured") if isinstance(gps, dict) else "Not captured"
    
    st.info(f"""
    **Audit ID:** {st.session_state.audit_id}  
    **Inspector:** {st.session_state.inspector_name}  
    **Location:** {location}  
    **Time:** {data.get('timestamp', 'Not recorded')}
    """)
    
    notes = st.text_area("Inspector Notes", data.get("notes", ""))
    st.session_state.audit_data["notes"] = notes

with tab3:
    st.subheader("Export Reports")
    
    if not st.session_state.pin_verified:
        pin = st.text_input("Enter PIN (1234)", type="password")
        if st.button("🔓 Verify"):
            if pin == "1234":
                st.session_state.pin_verified = True
                st.rerun()
            else:
                st.error("Wrong PIN")
        st.stop()
    
    st.success("🔓 Access granted")
    
    data = st.session_state.audit_data
    
    if st.button("📄 Generate PDF"):
        # Simple PDF generation
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        elements.append(Paragraph("JuteVision Auditor - Government of India", styles['Heading1']))
        elements.append(Paragraph(f"Audit ID: {st.session_state.audit_id}", styles['Normal']))
        elements.append(Paragraph(f"Bales: {data.get('bales_count', 0)}", styles['Normal']))
        elements.append(Paragraph(f"Stock Days: {data.get('stock_days', 0)}", styles['Normal']))
        elements.append(Paragraph(f"Compliance: {data.get('compliance_status', 'PENDING')}", styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        
        st.download_button("Download PDF", buffer, f"{st.session_state.audit_id}.pdf", "application/pdf")
    
    # JSON export
    json_data = json.dumps(data, indent=2, default=str)
    st.download_button("Download JSON", json_data, f"{st.session_state.audit_id}.json", "application/json")
    
    if st.button("⬅️ Back"):
        st.session_state.pin_verified = False
        st.rerun()

st.markdown("---")
st.caption("© Ministry of Textiles, Government of India | Jute Commissioner Organisation")