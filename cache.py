import pickle


class Cache:
    def __init__(self, path: str):
        self.path = path
        self.cache = set()

    def save(self):
        with open(self.path, 'wb') as f:
            pickle.dump(self.cache, f)

    def load(self, is_clear=False):
        if is_clear:
            self.cache = set()
            self.save()
        try:
            with open(self.path, 'rb') as f:
                self.cache = pickle.load(f, encoding="utf-8")
        except FileNotFoundError:
            self.load(is_clear=True)
