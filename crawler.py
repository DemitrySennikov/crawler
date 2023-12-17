from cache import Cache
from parse import download_url, HTML_parser, USER_AGENT

from threading import Thread, Lock, active_count

import urllib.parse
import os.path
import pathlib
import time
import sys
import urllib.robotparser as rob


class Crawler:
    def __init__(self, url: str, filters: set, not_visited: Cache, 
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
        self._robots = self._robot_parser(url)


    def work(self):
        try:
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
                    try:
                        new_task.start()
                    except KeyboardInterrupt:
                        sys.exit(0)
                    except Exception:
                        pass
                    count += 1
                    if count % 100 == 0:
                        self._lock.acquire()
                        self._visited.save()
                        self._not_visited.save()
                        self._lock.release()
        except KeyboardInterrupt:
            sys.exit(0)


    def _task(self, current_url):
        try:
            url, text = download_url(current_url, self._retry_max, 
                                    self._follow_redirects)
            if text is not None and "<html" in text.lower():
                parser = HTML_parser()
                parser.feed(text)
                self._update_links(str(url), parser.links)
                self._save_html(str(url), text)
        except KeyboardInterrupt:
            sys.exit(0)
            
            
    def _update_links(self, url, links):
        for link in links:
            try:
                parsed_link = urllib.parse.urlparse(link)
                if not parsed_link.netloc:
                    parsed_link = urllib.parse.urljoin(url, link)
                else:
                    parsed_link = parsed_link.geturl()
                if parsed_link not in self._visited.cache:
                    if any(not f(parsed_link) for f in self.filters):
                        continue
                    if not self._robots.can_fetch(USER_AGENT, url):
                        continue
                    self._lock.acquire()
                    self._not_visited.cache.add(parsed_link)
                    self._lock.release()
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception:
                continue


    def _save_html(self, url, text):
        try:
            parts = url.split('/')
            parts = list(filter(lambda x: x != '', parts[2:]))
            parts[-1] = parts[-1].split('?')[0]
            path = pathlib.Path('.'.join(parts))
            file_path = str(pathlib.Path('Saved/' + str(path) + '.html'))
            file_path = file_path.replace(':', '.').replace('&','.')
            print(url)
            print(file_path)
            if not os.path.isfile(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
        except KeyboardInterrupt:
            sys.exit(0)

    
    def _robot_parser(self, url):
        url_parse = urllib.parse.urlparse(url)
        rob_parser = rob.RobotFileParser()
        rob_parser.set_url(url_parse.scheme + "://" + 
                           url_parse.netloc + "/robots.txt")
        rob_parser.read()
        return rob_parser
