gcc ./ps/xor.c -shared -std=c99 -O3 -o ./ps/xor.lib
pyinstaller --onefile --add-data "ps/xor.lib";. pstools.py