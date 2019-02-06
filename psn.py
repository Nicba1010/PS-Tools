import binascii
import concurrent
import re
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Pattern, Callable, Set

import requests
import sqlalchemy
import urllib3
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.ddl import CreateTable

from models import Product, Language, Title, TitleName, TitleUpdateInfoUrl, Update, UpdatePackage

Base = declarative_base()
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ps3_regex: Pattern = re.compile("(?:(?:[BPVX][CL][AEHJKPU][BCDMSTVXZ])|(?:NP[AEHJKUIX][A-Z])|(?:MRTC))\d{5}")


def get_soup_for_code(code):
    # print("Getting soup for \"{}\"...".format(code))
    response = requests.get(
        "https://a0.ww.np.dl.playstation.net/tpl/np/{code}/{code}-ver.xml".format(
            code=code
        ),
        verify=False
    )
    if response.status_code != 404:
        return BeautifulSoup(response.content, 'xml')
    else:
        return None


def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'lxml')


# noinspection PyShadowingBuiltins
def get_update_for_id(id):
    soup = get_soup_for_code(id)
    if soup is None:
        return None
    try:
        return {
            'id': id,
            'title': soup.find('TITLE').text,
            'titles': [
                {'lang_id': int(x.name.split('_')[-1]), 'name': x.text}
                for x
                in soup.find_all(re.compile('TITLE_\d\d'))
            ],
            'update_info_url': soup.find('paramhip')['url'] if soup.find('paramhip') is not None else None,
            'update_info_urls': [
                {'lang_id': int(x.name.split('_')[-1]), 'url': x['url']}
                for x
                in soup.find_all(re.compile('paramhip_\d\d'))
            ],
            'updates': [
                {
                    'version': x['version'],
                    'ps3_system_ver': x.get_decompression_stream('ps3_system_ver', -1.0),
                    'packages': [
                        {
                            'url': x['url'],
                            'size': x['size'],
                            'sha1sum': binascii.unhexlify(x['sha1sum']),
                            'drm_type': x.get_decompression_stream('drm_type', 'local')
                        },
                        {
                            'url': x.find('url')['url'],
                            'size': x.find('url')['size'],
                            'sha1sum': binascii.unhexlify(x.find('url')['sha1sum']),
                            'drm_type': x.find('url').get_decompression_stream('drm_type', 'local')
                        }
                    ] if x.find('url') is not None else [
                        {
                            'url': x['url'],
                            'size': x['size'],
                            'sha1sum': binascii.unhexlify(x['sha1sum']),
                            'drm_type': x.get_decompression_stream('drm_type', 'local')
                        }
                    ]
                }
                for x
                in soup.find_all('package')
            ]
        }
    except Exception as e:
        print(e)
        raise Exception


stuff = []


def test():
    with open('valid.txt', 'r') as f:
        for line in f:
            soup = get_soup_for_code(line.strip())
            if soup is None:
                continue
            # stuff1 = list(set([tag.name for tag in soup.find_all()]))
            if soup.find('url') is not None:
                print(line.strip() + '-' + str(len(soup.find_all('package'))))
            # for s in stuff1:
            #     if s not in stuff:
            #         print(s + ' -> ' + line.strip())
            #         stuff.append(s)


# noinspection PyUnresolvedReferences
def psn_updates():
    print(sqlalchemy.__version__)
    Base.metadata.create_all(engine)
    # session = Session()
    print(CreateTable(Product.__table__).compile(engine))
    print(CreateTable(Title.__table__).compile(engine))
    print(CreateTable(TitleName.__table__).compile(engine))
    print(CreateTable(TitleUpdateInfoUrl.__table__).compile(engine))
    print(CreateTable(Language.__table__).compile(engine))
    print(CreateTable(Update.__table__).compile(engine))
    print(CreateTable(UpdatePackage.__table__).compile(engine))

    ids = open('valid1.txt', 'r').readlines()
    total = 0

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {
            executor.submit(get_update_for_id, id_.strip()): id_.strip() for id_ in ids
        }
        for future in concurrent.futures.as_completed(futures):
            id_ = futures[future]
            try:
                update = future.result()
            except Exception as e:
                raise e
            else:
                if update is None:
                    continue
                print('Successfully mapped data for updates of id {}'.format(id_))
                print(len(update['updates']))
                for u in update['updates']:
                    total += int(u['packages'][0]['size'])
                print(total)

                # t = session.query(Title).filter(Title.id == update['id']).one_or_none()
                t = None
                if t is None:
                    print("Title doesn't exist yet")
                    # product = Product(name=update['title'])
                else:
                    print("Title exists")


def game_tdb():
    total_pages: int = int(
        get_soup(
            "https://www.gametdb.com/PS3/List"
        ).find(
            text=re.compile('.*Page 1 of \d+.*')
        ).split(
            ' of '
        )[-1].split(
            ' '
        )[0]
    )
    print("Total GameTDB pages: {}".format(total_pages))
    for page in range(1, total_pages + 1):
        print("Processing page {}:".format(page))
        page_soup = get_soup("https://www.gametdb.com/PS3/List?q&p={}".format(page))
        for row in page_soup.find('table', {'class': ['DQedit notranslate']}).find_all('tr')[1:]:
            title_id = row.find('a').text.strip()
            title_name = row.find_all('td')[-1].text.strip()
            print("\t{} - {}".format(
                title_id, title_name
            ))


class PSNDLEntry(object):
    is_ps3: Callable[['PSNDLEntry'], bool] = lambda x: ps3_regex.match(x.title_id)

    def __init__(self, db_line: str):
        data: List[str] = db_line.split(';')
        self.title_id: str = data[0]
        self.name: str = data[1]
        self.type: str = data[2]
        self.region: str = data[3]
        self.url: str = data[4]
        self.rap_file_name: str = data[5]
        self.rap_data: str = data[6]
        self.description: str = data[7]
        self.uploader: str = data[8]


def psndl():
    data: str = requests.post("https://psndl.net/download-db").content.decode('utf-8')
    entries: List[PSNDLEntry] = list(filter(PSNDLEntry.is_ps3, map(lambda x: PSNDLEntry(x), data.splitlines())))
    types: Set[str] = set(map(lambda x: x.type, entries))
    regions: Set[str] = set(map(lambda x: x.region, entries))
    print('Count: {}'.format(len(entries)))
    print('All Types: {}'.format(types))
    print('All Regions: {}'.format(regions))


if __name__ == '__main__':
    psndl()

# titlepatch -> NPHB00010
# TITLE_01 -> NPHB00010
# tag -> NPHB00010
# package -> NPHB00010
# paramsfo -> NPHB00010
# TITLE -> NPHB00010
# paramhip_15 -> BCES00011
# paramhip_06 -> BCES00011
# TITLE_06 -> BCES00011
# TITLE_16 -> BCES00011
# TITLE_15 -> BCES00011
# TITLE_07 -> BCES00011
# paramhip_14 -> BCES00011
# paramhip_12 -> BCES00011
# paramhip_07 -> BCES00011
# paramhip_05 -> BCES00011
# TITLE_05 -> BCES00011
# paramhip_01 -> BCES00011
# paramhip_17 -> BCES00011
# TITLE_08 -> BCES00011
# TITLE_13 -> BCES00011
# TITLE_04 -> BCES00011
# TITLE_17 -> BCES00011
# TITLE_02 -> BCES00011
# TITLE_14 -> BCES00011
# TITLE_03 -> BCES00011
# paramhip -> BCES00011
# paramhip_02 -> BCES00011
# paramhip_13 -> BCES00011
# TITLE_12 -> BCES00011
# paramhip_04 -> BCES00011
# paramhip_03 -> BCES00011
# paramhip_08 -> BCES00011
# paramhip_16 -> BCES00011
# TITLE_00 -> NPJB00006
# TITLE_19 -> NPUO00025
# TITLE_09 -> NPEA00028
# TITLE_10 -> NPEA00028
# TITLE_11 -> NPEA00028
# paramhip_00 -> NPUP00041
# paramhip_11 -> NPUP00041
# paramhip_10 -> NPUP00041
# paramhip_09 -> NPUP00041
# url -> NPJB00099
# paramhip_18 -> NPJA00119
# TITLE_18 -> NPJA00123
