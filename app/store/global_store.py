import os
import re
import time

from app.services.key_collector import KeyCollector
from app.services.parser_rdb import RdbParser


def remove_bytes_char(bytes_char):
    return re.sub(r'^[xnt]|[0-9]', '', bytes_char)


class GlobalStore:
    """
    GlobalStore class
    """
    def __init__(self):
        self.elements = {}

    def set_elements(self, key, value, expiration=None):
        expiration_time = time.time() + expiration if expiration else None
        self.elements[key] = (value, expiration_time)
        print(f"Set key '{key}' to value '{value}' with expiration time {expiration_time}")

    def get_elements_by_key(self, key):
        print(f"Elements {self.elements}")
        if key not in self.elements:
            return None

        value, expiration_time = self.elements[key]

        if expiration_time and time.time() > expiration_time:
            print(f"Key '{key}' has expired, deleting from store.")
            del self.elements[key]
            return None

        return value

    def get_all_keys(self):
        current_time = time.time()
        valid_keys = []
        for key, (value, expiration_time) in self.elements.items():
            if not expiration_time or current_time <= expiration_time:
                valid_keys.append(key)
        return valid_keys


    def parse_key(self, rdb_file_path):
        collector = KeyCollector()
        parser = RdbParser(collector)
        print(f"Parsing RDB content...")

        parser.parse(rdb_file_path)

        items = collector.items
        keys = collector.keys

        decoded_items = [(key.decode('utf-8'), value.decode('utf-8'), int(expiry.timestamp() * 1000)) for key, value, expiry in items]
        decoded_keys = [key.decode('utf-8') for key in keys]

        print(f"Extracted values: {decoded_items}")
        print(f"Extracted keys: {decoded_keys}")

        return decoded_items

    def load_rdb_file(self, dir_path, filename):
        if dir_path and filename:
            rdb_file_path = os.path.join(dir_path, filename)
            if rdb_file_path and os.path.exists(rdb_file_path):
                keys = self.parse_key(rdb_file_path)
                for key, value, expiry in keys:
                    self.set_elements(key, value or None, expiry or None)
