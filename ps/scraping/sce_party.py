import binascii
import os
from datetime import datetime

from aenum import Enum
# noinspection PyProtectedMember
from bs4 import BeautifulSoup, Tag
from requests import Session

from ps.scraping.scraping_utils import download_file_post


class StackStorageDownloader(object):
    def __init__(self, url: str, path: str, file_name: str = None):
        self.url: str = url
        with Session() as s:
            csrf_soup: BeautifulSoup = BeautifulSoup(s.get(url).content, 'lxml')
            self.csrf_token: str = csrf_soup.find('meta', {'name': 'csrf-token'})['content']
            download_file_post(self.url.replace('/s/', '/public-share/') + '/download/', data={
                'CSRF-Token': self.csrf_token,
                'paths[]': '/'
            }, session=s, path=path, file_name=file_name)


class FirmwareType(Enum):
    SYSTEM = "fw_sys"
    SYSTEM_DECRYPTED = "fw_sys_dec"
    BETA = "fw_sys_beta"
    BETA_DECRYPTED = "fw_sys_beta_dec"
    TESTKIT = "fw_dex_testkit"
    TESTKIT_DECRYPTED = "fw_dex_testkit_dec"
    DEVKIT = "fw_dex_devkit"
    DEVKIT_DECRYPTED = "fw_dex_devkit_dec"


# noinspection PyShadowingBuiltins
class Firmware(object):
    details_url: str = "https://sce.party/content/modal/resourcedisplay.php?resource={version}&section={type}"

    def __init__(self, version: str, type: str, session: Session):
        self.version: str = version
        self.type: FirmwareType = FirmwareType(type)
        print("Firmware: {} - {}".format(self.version, self.type))

        soup: BeautifulSoup = BeautifulSoup(session.get(self.details_url.format(
            version=self.version,
            type=self.type.value
        )).content, 'lxml')

        release_date_tag: Tag = soup.find('strong', text="Release Date")
        if release_date_tag is not None:
            release_date_text = release_date_tag.parent.parent.find_all('td')[-1].text
            self.release_date: datetime = datetime.strptime(release_date_text, "%d-%m-%Y")
            print(f"\tRelease Date: {self.release_date.date()}")
        else:
            self.release_date: datetime = None
            print("\tRelease Date Missing")

        file_size_tag: Tag = soup.find('strong', text="Filesize")
        if file_size_tag is not None:
            file_size_text = release_date_tag.parent.parent.find_all('td')[-1].text
            self.file_size: int = int(file_size_text[:-2]) * 1024 * 1024
            print(f"\tFile Size: {self.file_size}")
        else:
            self.file_size: int = None
            print("\tFile Size Missing")

        md5_checksum_tag: Tag = soup.find('strong', text="MD5 Checksum")
        if md5_checksum_tag is not None:
            md5_checksum_text: str = md5_checksum_tag.parent.parent.find_all('td')[-1].text
            self.md5_checksum: bytes = binascii.unhexlify(md5_checksum_text)
            print(f"\tMD5 Checksum: {md5_checksum_text}")
        else:
            self.md5_checksum: bytes = None
            print("\tMD5 Checksum Missing")

        self.url: str = soup.find('a')['href']
        print(f"\tURL: {self.url}")

    def download(self, path: str, file_name: str = None):
        if 'stackstorage' in self.url:
            StackStorageDownloader(self.url, path, file_name=file_name)


total = 0

class SceParty(object):
    firmware_url = "https://sce.party/content/firmwares.php"

    def __init__(self, file_root: str):
        self.file_root: str = file_root
        with Session() as s:
            s.headers = {
                'x-requested-with': 'XMLHttpRequest'
            }
            soup: BeautifulSoup = BeautifulSoup(s.get(self.firmware_url).content, "lxml")
            for a in soup.find_all('a', {'id': 'resource-download'}):
                firmware: Firmware = Firmware(a['data-resource'], a['data-section'], s)
                path: str = os.path.join(self.file_root, firmware.type.name, firmware.version)
                os.makedirs(path, exist_ok=True)
                global total
                total += 1
                # firmware.download(path)


if __name__ == '__main__':
    SceParty("H:/PS4/Firmware/")
