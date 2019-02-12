import os
from binascii import unhexlify
from typing import Dict

name_codec_map: Dict[bytes, str] = dict()

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'naming_exceptions.txt'), 'r') as f:
    for line in f:
        arr = line.split(',')
        name_codec_map[unhexlify(arr[0])] = arr[1]
