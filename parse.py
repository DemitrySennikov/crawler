import httpx
from html.parser import HTMLParser

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.731 YaBrowser/23.11.1.731 Yowser/2.5 Safari/537.36"

def download_url(url: str, retry_max = 0, follow_redirects = False):
    retries = 0
    while retries <= retry_max:
        try:
            r = httpx.get(url, headers={"user-agent": USER_AGENT},
                          follow_redirects=follow_redirects)
            if r.status_code == httpx.codes.OK:
                return r.url, r.text
        except Exception:
            retries += 1
    return None, None


class HTML_parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def reset(self):
        super().reset()
        self.links.clear()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (name, value) in attrs:
                if name == "href":
                    self.links.append(value)
        