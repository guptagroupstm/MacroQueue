rm -r .\\dist\\
python -m PyInstaller --onedir --noconsole --icon=MacroQueueIcon.ico --additional-hooks-dir=. --add-data="MacroQueueIcon.ico;." --add-data="Bitmaps/*.bmp;Bitmaps" --add-data="Functions/*.py;Functions" --clean  MacroQueue.py
rm -r .\\__pycache__\\
rm -r .\\build\\
# mv .\\dist\\MacroQueue.exe ..
# rm -r .\\dist\\
rm MacroQueue.spec
