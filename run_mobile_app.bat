@echo off
cd /d "C:\Users\zheho\Desktop\form_ocr_backend"
echo Starting Mobile App...
echo.
echo Open: http://localhost:8501
echo Press Ctrl+C to stop
echo.
"C:\Users\zheho\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run mobile_app.py
pause