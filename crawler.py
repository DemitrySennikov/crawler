from cache import Cache
from parse import download_url, HTML_parser

from threading import Thread, Lock, active_count

import urllib.parse
import os.path
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
        while len(self._not_visited.cache) > 0 or active_count() > 1:
            if active_count() > self._threads_limit:
                time.sleep(0.01)
                continue
            if len(self._not_visited.cache) > 0:
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
            self._save_html(str(url), text)
            
            
    def _update_links(self, url, links):
        for link in links:
            try:
                parsed_link = urllib.parse.urlparse(link)
                if not parsed_link.netloc:
                    parsed_link = urllib.parse.urljoin(url, link)
                else:
                    parsed_link = parsed_link.geturl()
                if parsed_link not in self._visited.cache:
                    if not self.filters(parsed_link):
                        continue
                    self._lock.acquire()
                    self._not_visited.cache.add(parsed_link.geturl())
                    self._lock.release()
            except Exception:
                return


    def _save_html(self, url, text):
        parts = url.replace(':', '_').replace('&',  '_').split('/')[2:]
        path = pathlib.Path('/'.join(['Saved', *parts[:-1]]))
        name_file = parts[-1].split('?')[0]
        file_path = str(pathlib.Path(str(path) + name_file + '.html'))
        if not os.path.isfile(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
