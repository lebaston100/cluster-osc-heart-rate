call ".venv\Scripts\activate.bat"
mkdir _build
mkdir _dist
pyinstaller --noconfirm --clean --onefile --workpath "_build" --distpath "_dist" main.py