import time

class GlobalStore:
    def __init__(self):
        self.elements = {}

    def set_elements(self, key, value, expiration=None):
        expiration_time = time.time() + expiration if expiration else None
        self.elements[key] = (value, expiration_time)
        print(f"Set key '{key}' to value '{value}' with expiration time {expiration_time}")

    def get_elements_by_key(self, key):
        # Check if key exists
        if key not in self.elements:
            return None

        value, expiration_time = self.elements[key]

        if expiration_time and time.time() > expiration_time:
            print(f"Key '{key}' has expired")
            del self.elements[key]
            return None

        return value
