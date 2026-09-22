@echo off
setlocal

echo Building GPX to SHP Converter for Windows...
echo.

if not exist .venv (
    py -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

pyinstaller ^
  --noconfirm ^
  --clean ^
  --name "GPX_SHP_Converter" ^
  --onedir ^
  --collect-all streamlit ^
  --collect-all geopandas ^
  --collect-all pyogrio ^
  --collect-all pyproj ^
  --collect-all shapely ^
  --add-data "app.py;." ^
  --add-data "src;src" ^
  windows_launcher.py

echo.
echo Build complete.
echo Distribute the entire folder:
echo dist\GPX_SHP_Converter
echo.
pause
