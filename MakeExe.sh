rm -r .\\dist\\
# python -m PyInstaller --onedir --noconsole --icon=MacroQueueIcon.ico --additional-hooks-dir=. --add-data="MacroQueueIcon.ico;." --add-data="Bitmaps/*.bmp;Bitmaps"  --clean  MacroQueue.py
# --exclude-module=Functions --add-data="Functions/*.py;Functions"
python -m PyInstaller --onedir --noconsole --icon=MacroQueueIcon.ico  --add-data="MacroQueueIcon.ico;." --add-data="Bitmaps/*.bmp;Bitmaps"  --exclude-module=Functions --add-data="Functions/*.py;Functions" --add-data="Macros/*.json;Macros" --clean  MacroQueue.py
rm -r .\\__pycache__\\
rm -r .\\build\\
# mv .\\dist\\MacroQueue.exe ..
# rm -r .\\dist\\
rm MacroQueue.spec
