import os
import re
from typing import Dict

from requests import Session, Response


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

    if not os.path.exists(path) or os.stat(path).st_size != int(r.headers.get('Content-Length', default='-1')):
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=2 * 1024 * 1024):
                if chunk:
                    f.write(chunk)

    r.close()
    print(url + " has been downloaded!")
