from cache import Cache
from parse import download_url, HTML_parser

from threading import Thread, Lock, active_count

import urllib.parse
import pathlib
import time


class Crawler:
    def __init__(self, url: str, filters: list, not_visited: Cache, 
                 visited: Cache, retry_max: int, follow_redirects: bool,
                 threads_limit: int = 1000):
        self.url = url
        self.filters = filters
        self._not_visited = not_visited
        self._visited = visited
        self._lock = Lock()
        self._retry_max = retry_max
        self._follow_redirects = follow_redirects
        self._threads_limit = threads_limit


    def work(self):
        count = 0
        self._not_visited.cache.add(self.url)
        while len(self._not_visited) > 0 or active_count() > 1:
            if (active_count() > self._threads_limit or 
                len(self._not_visited.cache) == 0):
                time.sleep(1)
                continue
            self._lock.acquire()
            current_link = self._not_visited.cache.pop()
            self._visited.cache.add(current_link)
            self._lock.release()
            new_task = Thread(target=self._task, args=(current_link,))
            new_task.start()
            count += 1
            if count % 100 == 0:
                self._lock.acquire()
                self._visited.save()
                self._not_visited.save()
                self._lock.release()


    def _task(self, current_url):
        url, text = download_url(current_url, self._retry_max, 
                                 self._follow_redirects)
        if text is not None and "<html" in text.lower():
            parser = HTML_parser()
            parser.feed(text)
            self._update_links(url, parser.links)
            self._save_html(url, text)
            
            
    def _update_links(self, url, links):
        for link in links:
            try:
                parsed_link = urllib.parse.urlparse(link)
                if not parsed_link.netloc:
                    parsed_link = urllib.parse.urljoin(url, link)
                else:
                    parsed_link = parsed_link.geturl()
                if parsed_link not in self._visited.cache:
                    if any(not filter(parsed_link) for filter in self.filters):
                        continue
                    self._lock.acquire()
                    self._not_visited.cache.add(parsed_link.geturl())
                    self._lock.release()
            except Exception:
                pass


    def _save_html(self, url, text):
        parts = url.replace(':', '_').replace('&',  '_').split('/')[2:]
        path = pathlib.Path('/'.join(['Saved', *parts[:-1]]))
        path.mkdir(parents=True, exist_ok=True)
        name_file = parts[-1].split('?')[0]
        file_path = pathlib.Path(str(path) + name_file + '.html')
        file_path = urllib.parse.unquote(str(file_path))
        with open(str(file_path), 'w', encoding='utf-8') as f:
            f.write(text)
