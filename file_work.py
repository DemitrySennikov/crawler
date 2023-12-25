import pathlib
import os.path
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt

from threading import Lock


def save_html(url, text):
    try:
        parts = url.split('/')
        parts = list(filter(lambda x: x != '', parts[2:]))
        parts[-1] = parts[-1].split('?')[0]
        path = pathlib.Path('.'.join(parts))
        path = (str(path).replace('/', '.').replace('\\', '.')
                .replace(':', '.').replace('>', '.').replace('<', '.')
                .replace('*', '.').replace('?', '.').replace('|', '.')
                .replace('\"', '.'))
        file_path = str(pathlib.Path('Saved/' + path + '.html'))
        file_path = file_path.replace(':', '.').replace('&','.')
        print(url)
        print(file_path)
        print()
        if not os.path.isfile(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
    except KeyboardInterrupt:
        sys.exit(0)


def show_graph():
    try:
        with open("links.json", 'r', encoding='utf-8') as f:
            D = json.load(f)
    except FileNotFoundError:
        D = dict()
    G = nx.Graph(directed = True)
    for url in D:
        G.add_node(url)
        for link in D[url]:
            G.add_node(link)
            G.add_edge(url, link)
    nx.draw(G, with_labels = True)
    plt.show()


def add_links_to_graph(lock: Lock, url, links):
    lock.acquire()
    try:
        with open("links.json", 'r') as f:
            D = json.load(f)
    except FileNotFoundError:
        D = dict()
    D[url] = list(links)
    with open("links.json", 'w', encoding="utf-8") as f:
        json.dump(D, f, indent=4)
    lock.release()
