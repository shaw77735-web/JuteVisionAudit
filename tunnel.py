#!/usr/bin/env python3
"""
JuteVision Live Tunnel - Exposes Streamlit to 4G/Internet
"""
import subprocess
import time
import sys
import os

print("🚀 Starting JuteVision Streamlit app...")
print("This will be accessible from both Wi-Fi and 4G!\n")

# Start Streamlit
os.chdir("c:\\Users\\AFTAB\\Desktop\\New folder\\JuteVision")

cmd = [
    sys.executable, "-m", "streamlit", "run", "jute_test.py",
    "--server.port=8500",
    "--server.address=0.0.0.0",
    "--server.enableCORS=false",
    "--logger.level=info"
]

print("="*70)
print("✅ STREAMLIT IS RUNNING")
print("="*70)
print(f"\n📍 LOCAL ACCESS (Same Wi-Fi):")
print(f"   → http://192.168.0.185:8500")
print(f"\n📱 FOR 4G PHONE - Use one of these options:\n")
print(f"   OPTION 1: Use ngrok tunnel")
print(f"   → Open another terminal")
print(f"   → Run: ngrok http 8500")
print(f"   → Use the provided https://xxx.ngrok.io URL on your 4G phone\n")
print(f"   OPTION 2: Use localtunnel")
print(f"   → Open another terminal")
print(f"   → Run: npx localtunnel --port 8500")
print(f"   → Use the provided https://xxx.loca.lt URL on your 4G phone\n")
print(f"="*70)
print(f"Starting app now...\n")

# Start Streamlit
subprocess.run(cmd)
