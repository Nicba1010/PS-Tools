cd utils
gcc xor.c sha1.c -shared -std=c99 -O3 -o xor.win32.lib
cd ..
pyinstaller --onefile --add-data "./utils/xor.win32.lib";"utils" --add-data "./format/pkg/naming_exceptions.txt";"format/pkg" pstools.py