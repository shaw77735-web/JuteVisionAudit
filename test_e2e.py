import streamlit as st

# ... existing code ...

def display_settings():
    with st.popover("⚙️ Settings"):
        st.write("Stock settings")
        st.write("Floating arrow labels")

st.button(label="Profile", on_click=display_settings)

# White Header Fix
st.markdown("<h1 style='color: white;'>Hello, Inspector</h1>", unsafe_allow_html=True)

# Black Metric Text in Result Cards
def format_metric_card(metric_name, metric_value):
    st.metric(label=metric_name, value=metric_value, delta=None, help=None, color="#000000", icon=None)

# Smart Compliance Logic
def display_badge(jute_detected):
    if jute_detected:
        st.write("COMPLIANT", style="color: green; font-weight: bold;")
    else:
        st.write("NON-COMPLIANT", style="color: red; font-weight: bold;")

# Fix Terminal Error
st.markdown("**Note:** To ensure the tunnel starts correctly on this Windows machine, use `.\\cloudflared.exe` instead of `cloudflared`.")

# ... rest of code ...
git init

