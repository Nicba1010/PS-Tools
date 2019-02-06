import json
import time
from typing import List

from bs4 import BeautifulSoup
from requests import Session

from scraping.scraping_utils import download_file


class JonnySPScraper(object):
    base_url: str = "http://jonnysp.bplaced.net/"
    url: str = "{}data.php?draw=1&_=()&start=0&length=100000&columns%5B0%5D%5Bd%5D".format(
        base_url, int(time.time() * 1000)
    )

    def __init__(self, files_root: str):
        self.ird_urls: List[str] = []
        self.files_root: str = files_root
        with Session() as s:
            data = json.loads(s.get(self.url).content, encoding='UTF-8')
            for ird in data['data']:
                soup: BeautifulSoup = BeautifulSoup(ird['filename'], 'lxml')
                ird_url: str = self.base_url + soup.find('a')['href']
                self.ird_urls.append(ird_url)

        for ird_url in self.ird_urls:
            download_file(ird_url, path=self.files_root)


if __name__ == '__main__':
    JonnySPScraper(files_root="H:/IRD/")
