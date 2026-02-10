# Run JuteVision Industrial Hub (Streamlit)
$env:Path = "C:\Program Files\nodejs;" + $env:Path
cd $PSScriptRoot
.\venv\Scripts\Activate.ps1
pip install streamlit reportlab python-docx -q 2>$null
streamlit run jute_test.py --server.port 8501 --server.address 0.0.0.0
