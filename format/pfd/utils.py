from binascii import unhexlify
from typing import Dict, List


def load_secure_file_ids() -> Dict[str, bytes]:
    data: Dict[str, bytes] = {}
    with open('games.conf', 'r') as f:
        current_ids: List[str] = None
        for line in f:
            if line.startswith('['):
                current_ids = line[1:-1].split('/')
            elif line.startswith('secure_file_id'):
                for id_ in current_ids:
                    data[id_] = unhexlify(line.split('=')[1].strip())
    return data
