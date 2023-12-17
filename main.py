import argparse
import sys

from cache import Cache
from crawler import Crawler


arg_parse = argparse.ArgumentParser()
arg_parse.add_argument('--clear', type=bool, default=False, 
                       help='Clear cash')
arg_parse.add_argument('-u', '--url', type=str, help='Url for crawling')
arg_parse.add_argument('-c', '--retry_count', type=int, default=1, 
                       help='Max retry attempts for request')
arg_parse.add_argument('-r', '--follow_redirects', type=bool, default=True, 
                       help='Allow redirects, default True')
arg_parse.add_argument('-th', '--threads', type=int, default=1000, 
                       help='Max count threads')
arg_parse.add_argument('-fo', "--filter_only", type=str, default='', nargs='*',
                       help='Including filters')
arg_parse.add_argument('-fe', "--filter_exclusion", type=str, default='', 
                       nargs='*', help='Excluding filters')


def main(args):
    not_visited = Cache('not_visited.pickle')
    visited = Cache('visited.pickle')
    not_visited.load(is_clear=args.clear)
    visited.load(is_clear=args.clear)
    filters = set([lambda url: url not in args.filter_exclusion])
    if args.filter_only:
        filters.add(lambda url: url in args.filter_only)
    crawler = Crawler(args.url, filters, not_visited, visited, 
                      args.retry_count, args.follow_redirects, args.threads)
    try:
        crawler.work()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    args = arg_parse.parse_args()
    main(args)
