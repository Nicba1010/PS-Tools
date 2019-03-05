import concurrent
import os
import re
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, List, Generator, Union, Tuple

import requests
import urllib3
from requests import Session, Response

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def simple_get(url: str) -> Response:
    response: Response = requests.get(url, verify=False)
    return response


def multithread_get(urls: List[str], workers: int = 8) -> Generator[Union[Tuple[str, Response], None], None, None]:
    with ThreadPoolExecutor(max_workers=workers) as executor:
        print("Creating futures")
        futures = {
            executor.submit(simple_get, url): url for url in urls
        }
        print('Done creating futures')
        for future in concurrent.futures.as_completed(futures):
            url: str = futures[future]
            try:
                response: Response = future.result()
            except Exception as e:
                raise e
            else:
                if response is None:
                    yield None
                yield (url, response)


def download_file(url: str, session: Session = Session(), path: str = './', file_name: str = None):
    file_name: str = file_name if file_name is not None else url.split('/')[-1]
    r: Response = session.get(url, stream=True)
    with open(os.path.join(path, file_name), 'wb') as f:
        for chunk in r.iter_content(chunk_size=2 * 1024 * 1024):
            if chunk:
                f.write(chunk)
    print(url + " has been downloaded!")


def download_file_post(url: str, data: Dict, session: Session = Session(), path: str = './', file_name: str = None):
    r: Response = session.post(url, data=data, stream=True)

    file_name: str = file_name
    if file_name is None:
        if "Content-Disposition" in r.headers.keys():
            file_name = re.findall("filename=\"(.+)\"", r.headers["Content-Disposition"])[0]
        else:
            file_name = url.split("/")[-1]

    path: str = os.path.join(path, file_name)

    if not os.path.exists(path) or os.stat(path).st_size != int(
            r.headers.get_decompression_stream('Content-Length', default='-1')):
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=2 * 1024 * 1024):
                if chunk:
                    f.write(chunk)

    r.close()
    print(url + " has been downloaded!")
