import unittest
import json
import pickle
from re import search
from argparse import Namespace
from threading import Thread, active_count

from main import main
from cache import Cache
from crawler import Crawler


class TestMethods(unittest.TestCase):
    def setUp(self):
        self.not_visited = Cache('not_visited.pickle')
        self.visited = Cache('visited.pickle')
        self.not_visited.load()
        self.visited.load()
        self.not_visited_cache = set(self.not_visited.cache)
        self.visited_cache = set(self.visited.cache)
        try:
            with open("links.json", 'r') as f:
                self.links = json.load(f)
        except FileNotFoundError:
            self.links = dict()
        except json.decoder.JSONDecodeError:
            with open("links.json", 'w') as f:
                json.dump(dict(), f)
            self.links = dict()

    def test_no_redirects(self):
        args = Namespace(url = 'https://wikipedia.org', retry_count = 100,
             threads = 1000, clear = True, graph = False,
             no_redirects = True, filter_exclusion = "",
             filter_only = 'https://meta.wikimedia.org', HTML=False)
        task = Thread(target=main, args=(args,), daemon=True)
        task.start()
        task.join(5)

    def test_with_low_parameters(self):
        args = Namespace(url = 'https://wikipedia.org', retry_count = 1,
             threads = 10, clear = True, graph = False,
             no_redirects = False, filter_exclusion = "",
             filter_only = '', HTML=False)
        task = Thread(target=main, args=(args,), daemon=True)
        task.start()
        task.join(20)

    def test_with_high_parameters(self):
        args = Namespace(url = 'https://wikipedia.org', retry_count = 1000,
             threads = 10000, clear = True, graph = False,
             no_redirects = False, filter_exclusion = "",
             filter_only = '', HTML=False)
        task = Thread(target=main, args=(args,), daemon=True)
        task.start()
        task.join(20)

    def test_with_filters(self):
        args = Namespace(url = 'https://kadm.kmath.ru', retry_count = 10,
             threads = 1000, clear = True, graph = False,
             no_redirects = False, filter_exclusion = ".*/pages|.*/files",
             filter_only = 'https://kadm.kmath.ru', HTML=False)
        task = Thread(target=main, args=(args,), daemon=True)
        task.start()
        task.join(10)

    def test_end_work(self):
        args = Namespace(url = 'https://kadm.kmath.ru', retry_count = 10,
             threads = 1000, clear = True, graph = False,
             no_redirects = False, filter_exclusion = ".*/pages|.*/files",
             filter_only = 'https://kadm.kmath.ru', HTML=False)
        main(args)

    def tearDown(self):
        self.not_visited.cache = self.not_visited_cache
        self.visited.cache = self.visited_cache
        self.not_visited.save()
        self.visited.save()
        with open("links.json", 'w') as f:
            json.dump(self.links, f, indent=4)


if __name__ == "__main__":
    unittest.main()
