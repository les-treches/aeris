@echo off
title AERIS Environmental Intelligence Platform
echo Starting AERIS Dashboard...
cd /d "%~dp0"
python serve.py
pause
