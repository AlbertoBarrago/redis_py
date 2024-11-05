from app.services.parser_rdb import RdbCallback


class KeyCollector(RdbCallback):
    def __init__(self, string_escape = None):
        super().__init__(string_escape)
        self.items = []
        self.keys = []

    def set(self, key, value, expiry, info):
        self.keys.append(key)
        self.items.append((key,value))