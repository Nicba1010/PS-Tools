import os
import re
import shutil
from typing import List, Pattern, Callable

import requests

ps3_regex: Pattern = re.compile("(?:(?:[BPVX][CL][AEHJKPU][BCDMSTVXZ])|(?:NP[AEHJKUIX][A-Z])|(?:MRTC))\d{5}")


def human_size(size_: int, format_: str = '3.2'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size_) < 1024.0:
            return f"{size_:{format_}f} {unit}B"
        size_ /= 1024.0
    return f"{size_:.1f} YiB"


# noinspection PyShadowingBuiltins
class Entry(object):
    is_ps3: Callable[['Entry'], bool] = lambda x: ps3_regex.match(x.id)

    def __init__(self, id: str, region: str, name: str, link: str, rap: str, content_id: str):
        self.id: str = id
        self.region: str = region
        self.name: str = name
        self.link: str = link
        self.rap: str = rap
        self.content_id: str = content_id

    @staticmethod
    def from_nps_line(line: str):
        arr = line.split('\t')
        return Entry(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5])

    @staticmethod
    def from_psndl_line(line: str):
        arr = line.split(';')
        return Entry(arr[0], arr[3], arr[1], arr[4], arr[6], arr[5])

    def __repr__(self):
        return f'{self.id},{self.region},{self.name},{self.link},{self.content_id},{self.rap}'


entries: List[Entry] = []


def get_size(url: str) -> int:
    return int(requests.head(url).headers.get('content-length', 0))


def retard_dl(url: str, to: str):
    r = requests.post(url, allow_redirects=True)
    with open(to, 'wb') as f:
        f.write(r.content)
    print(f'Downloaded: {url}')


def load_nps(file: str):
    with open(file, 'r', encoding='UTF-8') as f:
        line_n = 0
        for line in f:
            if line_n == 0:
                line_n += 1
                continue
            entries.append(Entry.from_nps_line(line))
            print(entries[-1])


def load_psndl(file: str):
    with open(file, 'r', encoding='UTF-8') as f:
        for line in f:
            entries.append(Entry.from_psndl_line(line))
            print(entries[-1])


def deduplicate():
    new_entries: List[Entry] = []
    for entry in entries:
        exists: bool = False
        if entry.link == 'MISSING':
            continue
        for entry_ in new_entries:
            if entry.link == entry_.link:
                exists = True
                break
        if not exists:
            new_entries.append(entry)

    entries.clear()
    ps3_entries: List[Entry] = list(filter(Entry.is_ps3, new_entries))

    for entry in ps3_entries:
        entries.append(entry)
        print(entry)


def filter_downloaded():
    new_entries: List[Entry] = []
    for entry in entries:
        if not os.path.exists(f'H:\\PSNDL\\{os.path.basename(entry.link)}'):
            new_entries.append(entry)

    entries.clear()

    for entry in new_entries:
        entries.append(entry)
        print(entry)


total = 0
a = False

if __name__ == '__main__':

    if os.path.exists('./temp'):
        shutil.rmtree('./temp')
    os.makedirs('./temp')

    retard_dl('https://nopaystation.com/tsv/PS3_GAMES.tsv', './temp/PS3_GAMES.tsv')
    retard_dl('https://nopaystation.com/tsv/PS3_DLCS.tsv', './temp/PS3_DLCS.tsv')
    retard_dl('https://nopaystation.com/tsv/PS3_THEMES.tsv', './temp/PS3_THEMES.tsv')
    retard_dl('https://nopaystation.com/tsv/PS3_AVATARS.tsv', './temp/PS3_AVATARS.tsv')
    retard_dl('https://psndl.net/download-db', './temp/psndl.db')

    load_nps('./temp/PS3_GAMES.tsv')
    load_nps('./temp/PS3_DLCS.tsv')
    load_nps('./temp/PS3_THEMES.tsv')
    load_nps('./temp/PS3_AVATARS.tsv')
    load_psndl('./temp/psndl.db')
    print(len(entries))

    deduplicate()
    print(len(entries))

    filter_downloaded()
    print(len(entries))

    with open('./temp/out.txt', 'w') as f:
        for entry in entries:
            f.write(f'{entry.link}\n')
