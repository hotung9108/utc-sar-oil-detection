@echo off
chcp 65001 > nul
title Phat Hien Vet Dau Tran SAR - Web Workstation
echo ======================================================================
echo    HE THONG PHAT HIEN VET DAU TRAN TU ANH SAR SENTINEL-1
echo    KHOI DONG GIAO DIEN WEB STREAMLIT
echo ======================================================================
echo.
echo Dang khoi dong may chu tai http://localhost:8501...
echo.
python -m streamlit run web/app.py
pause
