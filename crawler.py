from cache import Cache
from parse import download_url, HTML_parser, USER_AGENT
from file_work import save_html, add_links_to_graph

from threading import Thread, Lock, active_count

import urllib.parse
import time
import sys
import urllib.robotparser as rob


class Crawler:
    def __init__(self, url: str, filters: set, not_visited: Cache, 
                 visited: Cache, retry_max: int, follow_redirects: bool,
                 threads_limit: int):
        self.url = url
        self.filters = filters
        self._not_visited = not_visited
        self._visited = visited
        self._lock = Lock()
        self.retry_max = retry_max
        self.follow_redirects = follow_redirects
        self.threads_limit = threads_limit


    def work(self):
        try:
            count = 0
            self._not_visited.cache.add(self.url)
            while len(self._not_visited.cache) > 0 or active_count() > 1:
                if active_count() > self.threads_limit:
                    time.sleep(0.01)
                    continue
                if len(self._not_visited.cache) > 0:
                    self._lock.acquire()
                    current_link = self._not_visited.cache.pop()
                    self._visited.cache.add(current_link)
                    self._lock.release()
                    new_task = Thread(target=self._task, args=(current_link,),
                                      daemon=True)
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
            url, text = download_url(current_url, self.retry_max, 
                                     self.follow_redirects)
            url = urllib.parse.unquote(str(url))
            parsed_url = urllib.parse.urlparse(url)
            if text is not None:
                parser = HTML_parser()
                parser.feed(text)
                save_html(url, text)
                links = parser.links
                for i in range(len(links)):
                    links[i] = urllib.parse.unquote(links[i])
                    if not links[i].startswith('http'):
                        if links[i].startswith('//'):
                            links[i] = (parsed_url.scheme + ':' + links[i])
                        else:
                            links[i] = (parsed_url.scheme + '://' + 
                                        parsed_url.netloc + '/' + links[i])
                links = set(links)
                add_links_to_graph(self._lock, url, links)
                self._update_links(url, links)
        except KeyboardInterrupt:
            sys.exit(0)
            
            
    def _update_links(self, url, links):
        robots = self._robot_parser(url)
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
                    if not robots.can_fetch(USER_AGENT, url):
                        continue
                    self._lock.acquire()
                    self._not_visited.cache.add(parsed_link)
                    self._lock.release()
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception:
                continue


    def _robot_parser(self, url):
        url_parse = urllib.parse.urlparse(url)
        rob_parser = rob.RobotFileParser()
        rob_parser.set_url(url_parse.scheme + "://" + 
                           url_parse.netloc + "/robots.txt")
        try:
            rob_parser.read()
        except Exception:
            pass
        return rob_parser
