import argparse
import re
import json

from cache import Cache
from crawler import Crawler
from file_work import show_graph


arg_parse = argparse.ArgumentParser()
arg_parse.add_argument('-u', '--url', type=str, help='Url for crawling')
arg_parse.add_argument('-rc', '--retry_count', type=int, default=10, 
                       help='Max retry attempts for request')
arg_parse.add_argument('-th', '--threads', type=int, default=1000, 
                       help='Max count threads')
arg_parse.add_argument('-fo', "--filter_only", type=str, default='', 
                       help='Including filters')
arg_parse.add_argument('-fe', "--filter_exclusion", type=str, default='', 
                       help='Excluding filters')
arg_parse.add_argument('-nr', '--no_redirects', action='store_false',
                       help='Disallow redirects')
arg_parse.add_argument('-c', '--clear', action='store_true', 
                       help='Clear cash')
arg_parse.add_argument('-g', '--graph', action='store_true', 
                       help='Show last saved graph')


def main(args):
    not_visited = Cache('not_visited.pickle')
    visited = Cache('visited.pickle')
    if args.graph:
        show_graph()
    not_visited.load(is_clear=args.clear)
    visited.load(is_clear=args.clear)
    if args.clear:
        with open("links.json", "w") as f:
            json.dump(dict(), f)
    if not args.url:
        return
    filters = set()
    if args.filter_exclusion:
        filters.add(lambda url: (re.search(rf"{args.filter_exclusion}", url)
                                 is None))
    if args.filter_only:
        filters.add(lambda url: (re.search(rf"{args.filter_only}", url)
                                 is not None))
    crawler = Crawler(args.url, filters, not_visited, visited, 
                      args.retry_count, args.no_redirects, args.threads)
    crawler.work()


if __name__ == "__main__":
    args = arg_parse.parse_args()
    main(args)
