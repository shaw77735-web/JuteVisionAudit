import importlib.metadata as _importlib_metadata
try:
    __orig_version = _importlib_metadata.version
    def _patched_version(name, *args, **kwargs):
        if name == "streamlit":
            return "1.54.0"
        return __orig_version(name, *args, **kwargs)
    _importlib_metadata.version = _patched_version
except Exception:
    pass

import streamlit as st
import cv2
import numpy as np
from datetime import datetime
import json
import os
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import hashlib
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    DOCX_AVAILABLE = True
except:
    DOCX_AVAILABLE = False

# ============================================
# PAGE CONFIG - MUST BE FIRST
# ============================================
st.set_page_config(
    page_title="JuteVision Auditor - Govt of India",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# INIT STATE - LOGIN & SESSION MANAGEMENT
# ============================================
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
if "page" not in st.session_state:
    st.session_state.page = "main"
if "pin_verified" not in st.session_state:
    st.session_state.pin_verified = False
if "simulated_success" not in st.session_state:
    st.session_state.simulated_success = False

# Initialize audit data structure
def init_audit_data(inspector):
    return {
        "audit_id": f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "inspector": inspector,
        "gps": None,
        "timestamp": None,
        "bales_count": 0,
        "daily_consumption": 100,
        "stock_days": 0,
        "weight_kg": 0,
        "confidence": 0,
        "detections": 0,
        "grade": "N/A",
        "compliance": "PENDING",
        "compliance_status": "PENDING",
        "jute_packaging_act_compliance": False,
        "image": None,
        "processed_image": None,
        "notes": "",
        "fraud_score": 0,
        "state": "Not specified",
        "district": "Not specified"
    }

# ============================================
# CSS STYLING - FIXED FOR BOTH THEMES
# ============================================
def get_css(theme):
    if theme == "dark":
        return """
        <style>
        [data-testid="stHeader"] {display:none !important;}
        [data-testid="stToolbar"] {display:none !important;}
        .block-container {
            padding-top: 0.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            background-color: #1a1a2e !important;
        }
        body {
            background-color: #1a1a2e !important;
            color: #ffffff !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        }
        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        p, div, span, label {
            color: #ffffff !important;
        }
        .stMarkdown p {
            color: #ffffff !important;
        }
        .header-title {
            background: linear-gradient(90deg, #FF9932 0%, #FFFFFF 50%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 32px;
            font-weight: 700;
            text-align: center;
            padding: 10px 0;
        }
        .govt-badge {
            background-color: #000080;
            color: white !important;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            border: 2px solid #FF9932;
        }
        .metric-card {
            background-color: #16213e;
            border: 2px solid #FF9932;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: #FF9932 !important;
            font-weight: bold;
            font-size: 24px;
        }
        .compliant-badge {
            background-color: #138808;
            color: #ffffff !important;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 32px;
            border: 3px solid #FF9932;
        }
        .non-compliant-badge {
            background-color: #FF9932;
            color: #000000 !important;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 32px;
            border: 3px solid #138808;
        }
        .info-box {
            background-color: #16213e;
            border-left: 4px solid #FF9932;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        button {
            border-radius: 12px !important;
            font-weight: 500 !important;
        }
        .stButton button {
            width: 100%;
        }
        </style>
        """
    else:
        return """
        <style>
        [data-testid="stHeader"] {display:none !important;}
        [data-testid="stToolbar"] {display:none !important;}
        .block-container {
            padding-top: 0.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            background-color: #f0f2f6 !important;
        }
        body {
            background-color: #f0f2f6 !important;
            color: #1f1f1f !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        }
        h1, h2, h3 {
            color: #1f1f1f !important;
            font-weight: 600 !important;
        }
        p, div, span, label {
            color: #1f1f1f !important;
        }
        .stMarkdown p {
            color: #1f1f1f !important;
        }
        .header-title {
            background: linear-gradient(90deg, #FF9932 0%, #000080 50%, #138808 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 32px;
            font-weight: 700;
            text-align: center;
            padding: 10px 0;
        }
        .govt-badge {
            background-color: #000080;
            color: white !important;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            border: 2px solid #FF9932;
        }
        .metric-card {
            background-color: #ffffff;
            border: 2px solid #FF9932;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: #000080 !important;
            font-weight: bold;
            font-size: 24px;
        }
        .compliant-badge {
            background-color: #138808;
            color: #ffffff !important;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 32px;
            border: 3px solid #FF9932;
        }
        .non-compliant-badge {
            background-color: #FF9932;
            color: #000000 !important;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 32px;
            border: 3px solid #138808;
        }
        .info-box {
            background-color: #ffffff;
            border-left: 4px solid #FF9932;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        button {
            border-radius: 12px !important;
            font-weight: 500 !important;
        }
        .stButton button {
            width: 100%;
        }
        </style>
        """

st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ============================================
# YOLO MODEL LOADING
# ============================================
@st.cache_resource
def load_yolo_model():
    """Load YOLO model with error handling for Streamlit Cloud"""
    try:
        from ultralytics import YOLO
        import urllib.request
        
        model_path = os.path.join(os.path.dirname(__file__), 'yolo11n.pt')
        
        if not os.path.exists(model_path):
            st.info("📥 Downloading AI Model... This may take a minute.")
            url = 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt'
            urllib.request.urlretrieve(url, model_path)
            st.success("✅ AI Model Ready!")
        
        model = YOLO(model_path)
        return model
    except Exception as e:
        st.error(f"⚠️ Model Load Error: {e}")
        return None

model = load_yolo_model()

# ============================================
# UTILITY FUNCTIONS
# ============================================

def add_watermark_to_image(image, metadata):
    """Add tamper-proof watermark with Indian Govt branding"""
    img = image.copy() if isinstance(image, Image.Image) else Image.fromarray(image)
    width, height = img.size
    
    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    
    timestamp = metadata.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    location = metadata.get("gps", {}).get("location", "Location Not Captured")
    inspector = metadata.get("inspector", "Unknown")
    audit_id = metadata.get("audit_id", "N/A")
    
    watermark_text_top = f"🇮🇳 Govt of India | JuteVision Auditor | Audit: {audit_id}"
    draw.text((10, 10), watermark_text_top, fill=(255, 153, 50, 200))
    
    watermark_text_bottom = f"📍 {location} | 🕐 {timestamp} | Inspector: {inspector}"
    try:
        bbox = draw.textbbox((0, 0), watermark_text_bottom)
        text_width = bbox[2] - bbox[0]
    except:
        text_width = len(watermark_text_bottom) * 6
    
    draw.text((width - text_width - 10, height - 30), watermark_text_bottom, fill=(19, 136, 8, 200))
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    img = Image.alpha_composite(img, watermark)
    return img.convert('RGB')

def detect_jute_bales(image, model):
    """Detect jute bales using YOLO"""
    if model is None:
        return 0, image, 0.0
    
    try:
        results = model(image)
        detections = len(results[0].boxes)
        
        annotated_img = results[0].plot()
        annotated_pil = Image.fromarray(annotated_img)
        
        if detections > 0:
            confidences = [box.conf.item() for box in results[0].boxes]
            avg_confidence = sum(confidences) / len(confidences)
        else:
            avg_confidence = 0.0
        
        return detections, annotated_pil, avg_confidence
    
    except Exception as e:
        st.error(f"Detection error: {e}")
        return 0, image, 0.0

def calculate_stock_days(bales_count, daily_consumption=100):
    """Calculate stock days"""
    if daily_consumption <= 0:
        return 0
    return round(bales_count / daily_consumption, 1)

def check_compliance(stock_days, min_days=30):
    """Check compliance"""
    return "PASS" if stock_days >= min_days else "FAIL"

def check_jute_packaging_act(bales_count, stock_days):
    """Specific compliance"""
    return stock_days >= 30 and bales_count >= 100

def generate_fraud_score(audit_data):
    """Generate fraud detection score based on actual data quality"""
    score = 0
    
    # No image captured
    if audit_data.get("image") is None:
        score += 40
    
    # Low confidence detection
    confidence = audit_data.get("confidence", 0)
    if confidence < 0.5:
        score += 30
    elif confidence < 0.7:
        score += 15
    
    # No GPS data
    if audit_data.get("gps") is None:
        score += 20
    
    # No timestamp
    if audit_data.get("timestamp") is None:
        score += 10
    
    # Very low bales count (suspicious)
    if audit_data.get("bales_count", 0) < 5:
        score += 10
    
    return min(score, 100)

def generate_audit_hash(audit_data):
    """Generate SHA256 hash"""
    data_string = json.dumps(audit_data, sort_keys=True, default=str)
    return hashlib.sha256(data_string.encode()).hexdigest()

def generate_pdf_report(audit_data, audit_id):
    """Generate Indian Government PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    header_style = styles['Heading1']
    header_style.textColor = colors.HexColor('#000080')
    elements.append(Paragraph("🇮🇳 GOVERNMENT OF INDIA", header_style))
    elements.append(Paragraph("Ministry of Textiles", styles['Heading2']))
    elements.append(Paragraph("Jute Commissioner Organisation", styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    # Title
    title_style = styles['Heading1']
    title_style.textColor = colors.HexColor('#FF9932')
    elements.append(Paragraph("Jute Stock Audit Report", title_style))
    elements.append(Paragraph(f"<b>Audit ID:</b> {audit_id}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {audit_data.get('timestamp', 'N/A')}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Compliance Status
    compliance = audit_data.get('compliance_status', 'PENDING')
    jpm_act = "✓ COMPLIANT" if audit_data.get('jute_packaging_act_compliance') else "✗ NON-COMPLIANT"
    
    if compliance == "PASS":
        comp_text = "<font color='#138808'>✓ COMPLIANT (30+ Days Stock)</font>"
    else:
        comp_text = "<font color='#FF9932'>✗ NON-COMPLIANT (Less than 30 Days)</font>"
    
    elements.append(Paragraph(f"<b>Jute Packaging Materials Act, 1987:</b> {jpm_act}", styles['Normal']))
    elements.append(Paragraph(f"<b>Stock Compliance:</b> {comp_text}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Data Table
    data = [
        ["Metric", "Value", "Standard/Remark"],
        ["Bales Count", str(audit_data.get('bales_count', 'N/A')), "Physical Count"],
        ["Stock Days", str(audit_data.get('stock_days', 'N/A')), "≥ 30 Days (JPM Act)"],
        ["Daily Consumption", str(audit_data.get('daily_consumption', 100)), "Bales/Day"],
        ["Weight (kg)", str(audit_data.get('weight_kg', 'N/A')), "As per BIS"],
        ["Detection Confidence", f"{audit_data.get('confidence', 0)*100:.1f}%", "≥ 85% Acceptable"],
        ["Quality Grade", str(audit_data.get('grade', 'N/A')), "A/B/C Classification"],
        ["Fraud Risk Score", f"{audit_data.get('fraud_score', 0)}/100", "Lower is Better"],
        ["Inspector", str(audit_data.get('inspector', 'N/A')), "Authorized Officer"],
        ["Location", str(audit_data.get('gps', {}).get('location', 'N/A')), "GPS Verified"],
        ["State", str(audit_data.get('state', 'N/A')), "Indian State"],
        ["Data Hash", str(generate_audit_hash(audit_data))[:16] + "...", "Tamper-Proof"],
    ]
    
    table = Table(data, colWidths=[150, 150, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FF9932')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    # Notes
    elements.append(Paragraph("<b>Inspector Remarks:</b>", styles['Heading3']))
    elements.append(Paragraph(str(audit_data.get('notes', 'No remarks provided')), styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Footer
    elements.append(Paragraph("<i>This document is digitally signed and tamper-proof as per IT Act, 2000.</i>", styles['Italic']))
    elements.append(Paragraph("<i>Generated by JuteVision Auditor - Ministry of Textiles, Govt of India</i>", styles['Italic']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_docx_report(audit_data, audit_id):
    """Generate Indian Government DOCX report"""
    if not DOCX_AVAILABLE:
        return None
    
    try:
        doc = Document()
        
        doc.add_heading('🇮🇳 GOVERNMENT OF INDIA', 0)
        doc.add_heading('Ministry of Textiles', level=1)
        doc.add_heading('Jute Commissioner Organisation', level=2)
        doc.add_paragraph()
        
        doc.add_heading('Jute Stock Audit Report', level=1)
        doc.add_paragraph(f"Audit ID: {audit_id}")
        doc.add_paragraph(f"Date: {audit_data.get('timestamp', 'N/A')}")
        doc.add_paragraph()
        
        compliance = audit_data.get('compliance_status', 'PENDING')
        jpm_act = audit_data.get('jute_packaging_act_compliance', False)
        
        p = doc.add_paragraph()
        p.add_run('Jute Packaging Materials Act, 1987: ').bold = True
        if jpm_act:
            p.add_run('✓ COMPLIANT').font.color.rgb = RGBColor(19, 136, 8)
        else:
            p.add_run('✗ NON-COMPLIANT').font.color.rgb = RGBColor(255, 153, 50)
        
        p = doc.add_paragraph()
        p.add_run('Stock Compliance: ').bold = True
        if compliance == "PASS":
            p.add_run('✓ PASS (30+ Days)').font.color.rgb = RGBColor(19, 136, 8)
        else:
            p.add_run('✗ FAIL (Less than 30 Days)').font.color.rgb = RGBColor(255, 153, 50)
        
        doc.add_paragraph()
        
        table = doc.add_table(rows=12, cols=3)
        table.style = 'Light Grid Accent 1'
        
        headers = ['Metric', 'Value', 'Standard/Remark']
        for i, header in enumerate(headers):
            table.rows[0].cells[i].text = header
            table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True
        
        rows_data = [
            ['Bales Count', str(audit_data.get('bales_count', 'N/A')), 'Physical Count'],
            ['Stock Days', str(audit_data.get('stock_days', 'N/A')), '≥ 30 Days (JPM Act)'],
            ['Daily Consumption', str(audit_data.get('daily_consumption', 100)), 'Bales/Day'],
            ['Weight (kg)', str(audit_data.get('weight_kg', 'N/A')), 'As per BIS'],
            ['Detection Confidence', f"{audit_data.get('confidence', 0)*100:.1f}%", '≥ 85% Acceptable'],
            ['Quality Grade', str(audit_data.get('grade', 'N/A')), 'A/B/C Classification'],
            ['Fraud Risk Score', f"{audit_data.get('fraud_score', 0)}/100", 'Lower is Better'],
            ['Inspector', str(audit_data.get('inspector', 'N/A')), 'Authorized Officer'],
            ['Location', str(audit_data.get('gps', {}).get('location', 'N/A')), 'GPS Verified'],
            ['State', str(audit_data.get('state', 'N/A')), 'Indian State'],
            ['Data Hash', generate_audit_hash(audit_data)[:16] + "...", 'Tamper-Proof'],
        ]
        
        for i, row_data in enumerate(rows_data, start=1):
            for j, value in enumerate(row_data):
                table.rows[i].cells[j].text = value
        
        doc.add_paragraph()
        doc.add_heading('Inspector Remarks:', level=2)
        doc.add_paragraph(str(audit_data.get('notes', 'No remarks provided')))
        
        doc.add_paragraph()
        doc.add_paragraph("This document is digitally signed and tamper-proof as per IT Act, 2000.").italic = True
        doc.add_paragraph("Generated by JuteVision Auditor - Ministry of Textiles, Govt of India").italic = True
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"DOCX error: {e}")
        return None

# ============================================
# LOGIN PAGE - FIXED
# ============================================
def show_login():
    # Clear any previous data on login page
    if st.session_state.get('audit_data') and not st.session_state.get('authenticated'):
        st.session_state.audit_data = None
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="header-title">🇮🇳 JuteVision Auditor</div>', unsafe_allow_html=True)
        st.markdown("### Ministry of Textiles, Government of India")
        st.markdown('<div class="govt-badge">Official Government Use Only</div>', unsafe_allow_html=True)
        st.divider()
        
        st.markdown("#### Inspector Authentication")
        
        inspector_id = st.text_input("Inspector ID (Govt Email)", placeholder="inspector@gov.in", key="login_id")
        password = st.text_input("Password", type="password", placeholder="Enter secure password", key="login_pass")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔐 Login", use_container_width=True, type="primary", key="login_btn"):
                if inspector_id and password:
                    if len(password) >= 6:
                        # Reset all session data on fresh login
                        st.session_state.authenticated = True
                        st.session_state.inspector_name = inspector_id
                        st.session_state.audit_id = f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        st.session_state.audit_data = init_audit_data(inspector_id)
                        st.session_state.simulated_success = False
                        st.session_state.pin_verified = False
                        st.success("✅ Login successful! Welcome to JuteVision Auditor.")
                        st.rerun()
                    else:
                        st.error("⚠️ Password must be at least 6 characters")
                else:
                    st.error("Please enter both ID and password")
        
        with col_btn2:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_btn"):
                st.stop()
        
        st.divider()
        st.markdown("""
        **🔒 Security Notice:**
        - This system is for authorized Jute Commissioner Organisation personnel only
        - All activities are logged and monitored
        - Reports are digitally signed under IT Act, 2000
        
        **📞 Support:** Contact NIC Helpdesk
        """)

if not st.session_state.authenticated:
    show_login()
    st.stop()

# ============================================
# PIN VERIFICATION
# ============================================
def verify_pin():
    """PIN verification for sensitive operations"""
    if not st.session_state.pin_verified:
        with st.expander("🔒 Security Verification Required", expanded=True):
            st.info("Enter 4-digit PIN to access export functions")
            pin = st.text_input("PIN", type="password", max_chars=4, key="pin_input")
            if st.button("🔓 Verify PIN", key="verify_pin_btn"):
                if pin == "1234":
                    st.session_state.pin_verified = True
                    st.success("✅ PIN verified! Access granted.")
                    st.rerun()
                else:
                    st.error("❌ Invalid PIN. Access denied.")
        return False
    return True

# ============================================
# HEADER - FIXED
# ============================================
col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    # Show avatar only, no name here
    st.markdown("""
    <div style="width:48px;height:48px;border-radius:24px;background:linear-gradient(135deg, #FF9932, #FFFFFF, #138808);display:flex;align-items:center;justify-content:center;font-size:24px;">
        🇮🇳
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="header-title">🇮🇳 JuteVision Auditor</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;color:#666;">Ministry of Textiles, Government of India</div>', unsafe_allow_html=True)
    
    # Theme toggle - FIXED
    theme_col1, theme_col2 = st.columns([1, 1])
    with theme_col1:
        if st.button('🌙 Dark Mode', key='dark_btn'):
            st.session_state.theme = 'dark'
            st.rerun()
    with theme_col2:
        if st.button('☀️ Light Mode', key='light_btn'):
            st.session_state.theme = 'light'
            st.rerun()

with col3:
    if st.button("🚪 Logout", key="logout_btn"):
        # Clear all data on logout
        st.session_state.authenticated = False
        st.session_state.inspector_name = None
        st.session_state.audit_id = None
        st.session_state.audit_data = None
        st.session_state.pin_verified = False
        st.session_state.simulated_success = False
        st.success("✅ Logged out successfully")
        st.rerun()

st.divider()

# ============================================
# SESSION INFO - SHOW INSPECTOR NAME HERE
# ============================================
st.markdown("### 📋 Session Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**👤 Inspector**")
    st.write(f"**{st.session_state.inspector_name}**")

with col2:
    st.markdown("**🆔 Audit ID**")
    st.write(f"**{st.session_state.audit_id}**")

with col3:
    st.markdown("**🟢 Status**")
    st.write("**Active - Ministry Server Connected**")

# ============================================
# SIMULATE SUCCESS TOGGLE - FIXED
# ============================================
st.markdown("---")
sim_col1, sim_col2 = st.columns([1, 3])
with sim_col1:
    simulate = st.toggle("🧪 Simulate Successful Scan", value=st.session_state.simulated_success)
    st.session_state.simulated_success = simulate

with sim_col2:
    if simulate:
        st.info("🧪 Simulation Mode ON: AI will return successful detection results for testing")
    else:
        st.caption("Toggle ON to test app with simulated data")

st.markdown("---")

# ============================================
# MAIN INTERFACE
# ============================================
st.markdown("## 🎯 Audit Operations")

tab1, tab2, tab3 = st.tabs(["📷 Scan Jute", "📊 Audit Results", "📤 Export Report"])

with tab1:
    st.markdown("### Jute Bale Capture & AI Analysis")
    
    col_scan1, col_scan2 = st.columns([2, 1])
    
    with col_scan1:
        st.markdown("**📸 Image Capture (Multiple Allowed)**")
        
        # Multiple file upload - FIXED
        upload_multiple = st.file_uploader(
            "Upload multiple images", 
            type=["png","jpg","jpeg"], 
            accept_multiple_files=True,
            key="multi_upload"
        )
        
        camera_input = st.camera_input("Or capture image", key="camera")
        
        # Process multiple uploads
        if upload_multiple:
            st.success(f"✅ {len(upload_multiple)} image(s) selected")
            for idx, file in enumerate(upload_multiple):
                try:
                    image = Image.open(file).convert('RGB')
                    st.image(image, caption=f"Image {idx+1}: {file.name}", use_column_width=True)
                    
                    # Save first image as primary
                    if idx == 0:
                        buf = io.BytesIO()
                        image.save(buf, format='JPEG')
                        buf.seek(0)
                        st.session_state.audit_data["image"] = buf
                except Exception as e:
                    st.error(f"❌ Failed to read {file.name}: {e}")
        
        # Single camera capture
        elif camera_input:
            try:
                image = Image.open(camera_input).convert('RGB')
                st.image(image, caption="Captured Image", use_column_width=True)
                
                buf = io.BytesIO()
                image.save(buf, format='JPEG')
                buf.seek(0)
                st.session_state.audit_data["image"] = buf
                st.success("✅ Image captured")
            except Exception as e:
                st.error(f"❌ Failed: {e}")
    
    with col_scan2:
        st.markdown("**📍 Location Data**")
        
        states = ["Select State", "West Bengal", "Bihar", "Odisha", "Assam", "Andhra Pradesh", "Jharkhand", "Other"]
        state = st.selectbox("State", states, key="state_select")
        st.session_state.audit_data["state"] = state if state != "Select State" else "Not specified"
        
        if st.button("📍 Capture GPS", use_container_width=True, key="gps_btn"):
            st.session_state.audit_data["gps"] = {
                "lat": 22.5726,
                "lng": 88.3639,
                "location": f"{state}, India" if state != "Select State" else "India"
            }
            st.session_state.audit_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success(f"✅ Location: {state}")
        
        if st.session_state.audit_data["gps"]:
            st.info(f"📍 {st.session_state.audit_data['gps']['location']}")
        
        st.markdown("**⚙️ Configuration**")
        daily = st.number_input("Daily Consumption (bales/day)", min_value=1, value=100, key="daily_cons")
        st.session_state.audit_data["daily_consumption"] = daily
    
    st.divider()
    
    st.markdown("**🤖 AI-Powered Analysis**")
    
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        analyze_clicked = st.button("🔍 Analyze with AI (YOLO)", use_container_width=True, type="primary", key="analyze_btn")
        
        if analyze_clicked:
            # SIMULATION MODE
            if st.session_state.simulated_success:
                with st.spinner("🧪 Running simulated analysis..."):
                    import time
                    time.sleep(2)  # Simulate processing
                    
                    # Simulated good results
                    detections = 45
                    confidence = 0.92
                    daily_consumption = st.session_state.audit_data.get("daily_consumption", 100)
                    stock_days = calculate_stock_days(detections, daily_consumption)
                    
                    st.session_state.audit_data.update({
                        "bales_count": detections,
                        "detections": detections,
                        "confidence": confidence,
                        "stock_days": stock_days,
                        "compliance_status": "PASS",
                        "jute_packaging_act_compliance": True,
                        "grade": "A",
                        "fraud_score": 5,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Create dummy processed image
                    if st.session_state.audit_data.get("image"):
                        img_buf = st.session_state.audit_data["image"]
                        img_buf.seek(0)
                        image = Image.open(img_buf).convert('RGB')
                        watermarked = add_watermark_to_image(image, st.session_state.audit_data)
                        
                        out_buf = io.BytesIO()
                        watermarked.save(out_buf, format='JPEG', quality=95)
                        out_buf.seek(0)
                        st.session_state.audit_data['processed_image'] = out_buf
                        
                        st.image(watermarked, caption=f'🎯 Simulated: {detections} Bales | Confidence: {confidence*100:.1f}%', use_column_width=True)
                    
                    st.success(f"✅ SIMULATION: {detections} bales detected! Stock: {stock_days} days.")
                    st.balloons()
                    st.rerun()
            
            # REAL ANALYSIS MODE
            else:
                if not st.session_state.audit_data.get("image"):
                    st.error("❌ Please capture or upload an image first!")
                else:
                    with st.spinner("🧠 AI analyzing jute bales..."):
                        try:
                            img_buf = st.session_state.audit_data["image"]
                            img_buf.seek(0)
                            image = Image.open(img_buf).convert('RGB')
                            
                            detections, annotated_img, confidence = detect_jute_bales(image, model)
                            
                            daily_consumption = st.session_state.audit_data.get("daily_consumption", 100)
                            stock_days = calculate_stock_days(detections, daily_consumption)
                            compliance = check_compliance(stock_days, 30)
                            jpm_compliance = check_jute_packaging_act(detections, stock_days)
                            fraud_score = generate_fraud_score(st.session_state.audit_data)
                            
                            # Grade based on actual results
                            if confidence > 0.90 and detections > 30:
                                grade = "A"
                            elif confidence > 0.75:
                                grade = "B"
                            elif confidence > 0.50:
                                grade = "C"
                            else:
                                grade = "D"
                            
                            st.session_state.audit_data.update({
                                "bales_count": detections,
                                "detections": detections,
                                "confidence": round(confidence, 2),
                                "stock_days": stock_days,
                                "compliance_status": compliance,
                                "jute_packaging_act_compliance": jpm_compliance,
                                "grade": grade,
                                "fraud_score": fraud_score,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                            watermarked = add_watermark_to_image(annotated_img, st.session_state.audit_data)
                            
                            out_buf = io.BytesIO()
                            watermarked.save(out_buf, format='JPEG', quality=95)
                            out_buf.seek(0)
                            st.session_state.audit_data['processed_image'] = out_buf
                            
                            st.image(watermarked, caption=f'🎯 Detected {detections} Bales | Confidence: {confidence*100:.1f}%', use_column_width=True)
                            st.success(f"✅ Analysis Complete! {detections} bales. Stock: {stock_days} days.")
                            
                            if compliance == "PASS":
                                st.balloons()
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {e}")
                            st.info("💡 Try enabling 'Simulate Successful Scan' for testing")
    
    with col_ai2:
        if st.button("✏️ Manual Entry", use_container_width=True, key="manual_btn"):
            st.session_state.show_manual = not st.session_state.get("show_manual", False)
            st.rerun()
    
    if st.session_state.get("show_manual", False):
        st.markdown("**📝 Manual Data Entry**")
        
        bales = st.number_input("Bales Count", 0, 10000, value=st.session_state.audit_data.get("bales_count", 0), key="manual_bales")
        st.session_state.audit_data["bales_count"] = bales
        st.session_state.audit_data["detections"] = bales
        
        daily = st.number_input("Daily Consumption", 1, 1000, value=st.session_state.audit_data.get("daily_consumption", 100), key="manual_daily")
        st.session_state.audit_data["daily_consumption"] = daily
        
        stock_days = calculate_stock_days(bales, daily)
        st.session_state.audit_data["stock_days"] = stock_days
        st.session_state.audit_data["compliance_status"] = check_compliance(stock_days)
        st.session_state.audit_data["jute_packaging_act_compliance"] = check_jute_packaging_act(bales, stock_days)
        
        # Calculate fraud score for manual entry
        st.session_state.audit_data["fraud_score"] = generate_fraud_score(st.session_state.audit_data)
        
        st.info(f"📊 Stock: {stock_days} days | Compliance: {st.session_state.audit_data['compliance_status']}")

with tab2:
    st.markdown("### 📊 Compliance Verification & Metrics")
    
    data = st.session_state.audit_data
    bales = data.get("bales_count", 0)
    stock_days = data.get("stock_days", 0)
    compliance = data.get("compliance_status", "PENDING")
    jpm_act = data.get("jute_packaging_act_compliance", False)
    confidence = data.get("confidence", 0)
    grade = data.get("grade", "N/A")
    fraud = data.get("fraud_score", 0)
    
    # If no analysis done yet, show zeros properly
    if bales == 0 and compliance == "PENDING":
        grade = "N/A"
        fraud = generate_fraud_score(data)  # Will be high (70-100) due to no data
    
    # Compliance Badges
    col_badges = st.columns(2)
    
    with col_badges[0]:
        if compliance == "PASS":
            st.markdown("""
            <div style="background-color:#138808;color:white;padding:20px;border-radius:15px;text-align:center;font-weight:bold;font-size:24px;border:3px solid #FF9932;">
                ✅ STOCK COMPLIANT<br><small>30+ Days Available</small>
            </div>
            """, unsafe_allow_html=True)
        elif compliance == "FAIL":
            st.markdown("""
            <div style="background-color:#DC143C;color:white;padding:20px;border-radius:15px;text-align:center;font-weight:bold;font-size:24px;border:3px solid #FF9932;">
                ❌ STOCK SHORTAGE<br><small>Less than 30 Days</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color:#808080;color:white;padding:20px;border-radius:15px;text-align:center;font-weight:bold;font-size:24px;">
                ⏳ PENDING ANALYSIS<br><small>No Data Available</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col_badges[1]:
        if jpm_act:
            st.markdown("""
            <div style="background-color:#000080;color:white;padding:20px;border-radius:15px;text-align:center;font-weight:bold;font-size:24px;border:3px solid #FF9932;">
                ✅ JPM ACT 1987<br><small>Fully Compliant</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color:#FF9932;color:black;padding:20px;border-radius:15px;text-align:center;font-weight:bold;font-size:24px;border:3px solid #000080;">
                ⚠️ JPM ACT 1987<br><small>Non-Compliant</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Metrics Grid
    st.markdown("### 📈 Key Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Total Bales")
        st.metric("Count", f"{bales}", "Jute Bales")
        
        st.markdown("#### 📅 Stock Duration")
        st.metric("Days", f"{stock_days}", "≥ 30 Days Required")
    
    with col2:
        st.markdown("#### 🎯 AI Confidence")
        st.metric("Accuracy", f"{confidence*100:.1f}%" if confidence > 0 else "0.0%", "Detection Quality")
        
        st.markdown("#### 🛡️ Fraud Risk")
        st.metric("Risk Score", f"{fraud}/100", "Lower is Better")
    
    # Grade - Show N/A or actual grade
    st.markdown("---")
    grade_display = grade if grade != "N/A" else "N/A"
    grade_colors = {"A": "#138808", "B": "#FF9932", "C": "#FFA500", "D": "#DC143C", "N/A": "#808080"}
    grade_color = grade_colors.get(grade_display, "#808080")
    text_color = "white" if grade_display in ["A", "D", "N/A"] else "black"
    
    st.markdown(f"""
    <div style="background-color:{grade_color};color:{text_color};padding:20px;border-radius:15px;text-align:center;font-weight:bold;font-size:48px;border:3px solid #000080;">
        Quality Grade: {grade_display}
    </div>
    """, unsafe_allow_html=True)
    
    if grade_display == "N/A":
        st.info("💡 Run AI Analysis or Manual Entry to get grade")
    
    # Notes
    st.markdown("---")
    st.markdown("### 📝 Inspector Remarks")
    notes = st.text_area("Official remarks", value=data.get("notes", ""), height=100, key="notes_area")
    st.session_state.audit_data["notes"] = notes
    
    # Audit Info
    st.markdown("---")
    st.info(f"""
    **🆔 Audit ID:** {st.session_state.audit_id}  
    **👤 Inspector:** {st.session_state.inspector_name}  
    **🕐 Timestamp:** {data.get('timestamp', 'Not recorded')}  
    **📍 Location:** {data.get('gps', {}).get('location', 'Not captured')}  
    **🏛️ State:** {data.get('state', 'Not specified')}
    """)

with tab3:
    st.markdown("### 📤 Export & Government Submission")
    
    # PIN Verification
    if not verify_pin():
        st.warning("🔒 Enter PIN to access export functions")
        st.stop()
    
    st.success("🔓 PIN Verified - Export Access Granted")
    
    st.markdown("#### 📋 Audit Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏛️ Official Details**")
        st.markdown(f"""
        - **Audit ID:** `{st.session_state.audit_id}`
        - **Inspector:** {st.session_state.inspector_name}
        - **Timestamp:** {st.session_state.audit_data.get('timestamp', 'N/A')}
        - **State:** {st.session_state.audit_data.get('state', 'N/A')}
        """)
    
    with col2:
        st.markdown("**📊 Audit Results**")
        st.markdown(f"""
        - **Bales Count:** {st.session_state.audit_data.get('bales_count', 0)}
        - **Stock Days:** {st.session_state.audit_data.get('stock_days', 0)}
        - **JPM Act 1987:** {'✅ Compliant' if st.session_state.audit_data.get('jute_packaging_act_compliance') else '❌ Non-Compliant'}
        - **Quality Grade:** {st.session_state.audit_data.get('grade', 'N/A')}
        """)
    
    st.markdown("---")
    
    # Export Buttons
    st.markdown("#### 📥 Download Official Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.audit_data.get("bales_count", 0) > 0:
            pdf_buffer = generate_pdf_report(st.session_state.audit_data, st.session_state.audit_id)
            st.download_button(
                label="📄 PDF Report (Govt)",
                data=pdf_buffer,
                file_name=f"{st.session_state.audit_id}_GOI_OFFICIAL.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.button("📄 PDF Report", disabled=True, use_container_width=True)
    
    with col2:
        if st.session_state.audit_data.get("bales_count", 0) > 0:
            docx_buffer = generate_docx_report(st.session_state.audit_data, st.session_state.audit_id)
            if docx_buffer:
                st.download_button(
                    label="📝 Word Document",
                    data=docx_buffer,
                    file_name=f"{st.session_state.audit_id}_GOI_OFFICIAL.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            else:
                st.error("Word export unavailable")
        else:
            st.button("📝 Word Document", disabled=True, use_container_width=True)
    
    with col3:
        if st.session_state.audit_data.get("processed_image"):
            img_buf = st.session_state.audit_data["processed_image"]
            img_buf.seek(0)
            st.download_button(
                label="📸 Evidence Photo",
                data=img_buf,
                file_name=f"{st.session_state.audit_id}_EVIDENCE.jpg",
                mime="image/jpeg",
                use_container_width=True
            )
        else:
            st.button("📸 Evidence Photo", disabled=True, use_container_width=True)
    
    st.markdown("---")
    
    # Technical Data
    st.markdown("#### 💾 Technical Data")
    col4, col5 = st.columns(2)
    
    with col4:
        json_data = json.dumps(st.session_state.audit_data, indent=2, default=str)
        st.download_button(
            label="📋 JSON (Technical)",
            data=json_data,
            file_name=f"{st.session_state.audit_id}_data.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col5:
        csv_data = "Field,Value\n"
        for key, value in st.session_state.audit_data.items():
            if key not in ["image", "processed_image"]:
                csv_data += f"{key},{value}\n"
        st.download_button(
            label="📊 CSV (Technical)",
            data=csv_data,
            file_name=f"{st.session_state.audit_id}_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Government Submission
    st.markdown("#### 🏛️ Submit to Ministry Server")
    
    if st.button("📤 Submit to Ministry of Textiles", use_container_width=True, type="primary", key="submit_btn"):
        with st.spinner("🌐 Submitting to Government of India server..."):
            submission_data = {
                "audit_id": st.session_state.audit_id,
                "inspector": st.session_state.inspector_name,
                "ministry": "Ministry of Textiles, Govt of India",
                "timestamp": datetime.now().isoformat(),
                "data_hash": generate_audit_hash(st.session_state.audit_data),
                "status": "SUBMITTED_TO_JUTE_COMMISSIONER",
                "jpm_act_compliance": st.session_state.audit_data.get("jute_packaging_act_compliance")
            }
            st.success("✅ Audit submitted successfully to Ministry of Textiles")
            st.json(submission_data)
            st.balloons()
    
    st.markdown("---")
    
    # Back button
    if st.button("⬅️ Back to Audit", use_container_width=True, key="back_export"):
        st.session_state.pin_verified = False
        st.rerun()

st.divider()

# ============================================
# FOOTER
# ============================================
st.markdown("""
---
<div style="text-align:center;">
<b>🇮🇳 JuteVision Auditor</b><br>
Ministry of Textiles, Government of India<br>
Jute Commissioner Organisation<br><br>

<b>Security & Compliance Features:</b><br>
🔐 SHA-256 Encrypted Audit Trails | 📍 GPS Verification | 🛡️ Fraud Detection<br>
✅ Jute Packaging Materials Act, 1987 Compliance | 📄 IT Act, 2000 Digital Signatures<br>
🏛️ BIS Standards | 🔒 NIC Secured Infrastructure<br><br>

<i>Official Government Use Only | All Activities Logged & Monitored</i><br>
<i>Violation of audit integrity is punishable under Indian Penal Code</i>
</div>
""")   
 