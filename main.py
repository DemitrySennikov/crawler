import argparse

from cache import Cache
from crawler import Crawler


arg_parse = argparse.ArgumentParser()
arg_parse.add_argument('-u', '--url', type=str, help='Url for crawling')
arg_parse.add_argument('-rc', '--retry_count', type=int, default=1, 
                       help='Max retry attempts for request')
arg_parse.add_argument('-th', '--threads', type=int, default=1000, 
                       help='Max count threads')
arg_parse.add_argument('-fo', "--filter_only", type=str, default='', nargs='*',
                       help='Including filters')
arg_parse.add_argument('-fe', "--filter_exclusion", type=str, default='', 
                       nargs='*', help='Excluding filters')
arg_parse.add_argument('-r', '--follow_redirects', action='store_true',
                       help='Allow redirects, default False')
arg_parse.add_argument('-c', '--clear', action='store_true', 
                       help='Clear cash')


def main(args):
    not_visited = Cache('not_visited.pickle')
    visited = Cache('visited.pickle')
    not_visited.load(is_clear=args.clear)
    visited.load(is_clear=args.clear)
    if not args.url:
        return
    filters = set([lambda url: 
                   all(not url.startswith(f) for f in args.filter_exclusion)])
    if args.filter_only:
        filters.add(lambda url:
                   any(url.startswith(f) for f in args.filter_only))
    crawler = Crawler(args.url, filters, not_visited, visited, 
                      args.retry_count, args.follow_redirects, args.threads)
    crawler.work()


if __name__ == "__main__":
    args = arg_parse.parse_args()
    main(args)
