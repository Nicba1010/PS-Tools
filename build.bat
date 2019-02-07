gcc ./utils/xor.c -shared -std=c99 -O3 -o ./utils/xor.win.lib
pyinstaller --onefile --add-data "./utils/xor.win.lib";. pstools.py