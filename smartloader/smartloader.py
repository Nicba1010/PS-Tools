from __future__ import annotations

from typing import Union, List, Tuple

from aenum import Enum
from requests import Session


class Method(Enum):
    GET = 'GET'
    POST = 'POST'


def human_size(size_: int, format_: str = '3.5'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size_) < 1024.0:
            return f"{size_:{format_}f} {unit}B"
        size_ /= 1024.0
    return f"{size_:.1f} YiB"


class SmartLoader(object):
    def __init__(self, url: str, method: Union[str, Method] = Method.GET, session: Session = Session(),
                 payload: Union[dict, None] = None, thread_count: Union[int, None] = None,
                 chunk_size: Union[int, None] = None):
        self.url: str = url
        self.session: Session = session
        self.method: Method = Method(method) if isinstance(method, str) else method
        self.payload: Union[dict, None] = payload if method is Method.POST else None
        self.size: int = None
        self.range_supported: bool = False
        self.ranges: List[Tuple[int, int]] = []

        # Load size and range support
        self.load_header_info()
        if not self.range_supported and (thread_count is not None or chunk_size is not None):
            print("Server does not support ranges, 1 thread will be used...")
            self.thread_count: int = 1
        else:
            if chunk_size is None and thread_count is not None:
                self.thread_count = thread_count
                chunk_size: int = int(self.size / thread_count)
                for chunk_start in range(0, self.size, chunk_size):
                    chunk_end: int = chunk_start + chunk_size
                    chunk_range: Tuple[int, int] = (chunk_start, chunk_end)
                    if chunk_end > self.size:
                        self.ranges[-1] = (self.ranges[-1][0], self.size)
                    else:
                        self.ranges.append(chunk_range)
            elif chunk_size is None and thread_count is None:
                self.thread_count: int = 1
            elif chunk_size is not None:
                self.thread_count = thread_count if thread_count is not None else 1
                self.ranges = list([
                    (x, (x + chunk_size) if x + chunk_size < self.size else self.size)
                    for x
                    in range(0, self.size, chunk_size)
                ])

        print(f"Initializing {self.thread_count} download threads...")
        for download_range in self.ranges:
            start: int = download_range[0]
            stop: int = download_range[1]
            print(f"Downloading range {human_size(start)} - {human_size(stop)}")

    @property
    def size_human(self) -> str:
        return human_size(self.size)

    def load_header_info(self) -> None:
        if self.size is None:
            if self.method == Method.GET:
                headers = self.session.head(self.url).headers
                self.size = int(headers.get('Content-Length', -1))
                self.range_supported = 'Accept-Ranges' in headers
            else:
                raise NotImplementedError


if __name__ == '__main__':
    sl: SmartLoader = SmartLoader("http://ipv4.download.thinkbroadband.com/1GB.zip", thread_count=8)
    print(sl.size_human)
