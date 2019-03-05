from binascii import hexlify
from typing import Generator, List

from bs4 import BeautifulSoup, Tag
from requests import Response

from scraping.scraping_utils import multithread_get
from utils.keys import PSP2_GAME_UPDATE_HMAC_KEY
from utils.utils import hmac_sha256


def generate_update_link(title_id: str) -> str:
    hash_val: str = hexlify(hmac_sha256(PSP2_GAME_UPDATE_HMAC_KEY, f"np_{title_id}".encode('ASCII'))).decode('ASCII')
    return f"https://gs-sec.ww.np.dl.playstation.net/pl/np/{title_id}/{hash_val}/{title_id}-ver.xml"


url = "https://gs-sec.ww.np.dl.playstation.net/pl/np/%tid%/%hash%/%tid%-ver.xml"
pkey = bytes([229, 226, 120, 170, 30, 227, 64, 130, 160, 136, 39, 156, 131, 249, 187, 200, 6, 130, 28, 82, 242, 171,
              93, 43, 74, 189, 153, 84, 80, 53, 81, 20
              ])


def generate_all_possible_title_ids() -> Generator[str, None, None]:
    for character in ['C', 'F', 'G', 'D', 'E', 'B', 'H', 'I', 'A', 'F']:
        for i in range(100000):
            yield f'PCS{character}{str(i).zfill(5)}'
        print(f"Generated for PCS{character}XXXXX")


if __name__ == '__main__':
    # print(generate_update_link('PCSE00491'))
    ids: List[str] = list(generate_update_link(title_id) for title_id in generate_all_possible_title_ids())
    print(f"Generated all update links")
    changeinfo_hashes: List[str] = []
    for pair in multithread_get(ids, workers=32):
        if pair is None:
            continue

        url: str = pair[0]
        title_id: str = url.split('/')[5]
        response: Response = pair[1]

        print(f'{title_id} -> {response.status_code}')

        if response.status_code != 200:
            continue

        soup: BeautifulSoup = BeautifulSoup(response.content, 'html5lib')

        changeinfo: Tag = soup.find('changeinfo')
        if changeinfo is None:
            print(soup.prettify())
            continue

        changeinfo_hash: str = changeinfo['url'].split('/')[-2]
        print(changeinfo_hash)
        changeinfo_hashes.append(changeinfo_hash)

    with open('changeinfo_hashes.txt', 'w') as f:
        for changeinfo_hash in changeinfo_hashes:
            f.write(f'{changeinfo_hash}\n')
