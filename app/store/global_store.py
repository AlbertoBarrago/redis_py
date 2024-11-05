import os
import time


def remove_bytes_char(bytes_char):
    if bytes_char.startswith("x"):
        return bytes_char[3:]
    elif bytes_char.startswith("t"):
        return bytes_char[2:]


def parse_key(rdb_content):
    split_content = rdb_content.split("\\")
    resize_key = split_content.index("xfb")

    key_index = resize_key + 4
    value_index = key_index + 1

    key_bytes = split_content[key_index]
    value_bytes = split_content[value_index]

    key = remove_bytes_char(key_bytes)
    value = remove_bytes_char(value_bytes)

    print(f"Key: {key} Value: {value}")
    return key, value


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

    def load_rdb_file(self, dir_path, filename):
        if dir_path and filename:
            rdb_file_path = os.path.join(dir_path, filename)
            if rdb_file_path and os.path.exists(rdb_file_path):
                with open(rdb_file_path, 'rb') as f:
                    rdb_content = str(f.read())
                    if rdb_content:
                        key = parse_key(rdb_content)
                        self.set_elements(key[0], key[1])
                        return "*1\r\n${}\r\n{}\r\n".format(len(key), key).encode()

        return "*0\r\n".encode()
