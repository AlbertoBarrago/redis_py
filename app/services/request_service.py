class RequestService:
    def __init__(self, data = None, encoding="utf-8", store=None):
        self.data = data
        self.encoding = encoding
        self.running = True
        self.store = store

    def parse_request(self, data):
        if data == b"$-1\r\n":
            return data
        separator = "\r\n"
        encoded = f"+{data}{separator}"
        print(f"encoded: {encoded}")
        return encoded.encode(encoding=self.encoding)

    def handle_client(self, client_socket):
        try:
            while self.running:
                self.data = client_socket.recv(1024)

                if not self.data:
                    break

                print("Received {!r}".format(self.data))
                elements = [el for el in self.data.split(b"\r\n") if el]
                if not elements:
                    continue

                print(f"Elements: {elements}")

                command = elements[2].decode('utf-8')
                print(f"Command: {command}")

                if command == "PING":
                    resp = self.parse_request("PONG")
                    print(f"Sending PONG response -> {resp}")
                    client_socket.sendall(resp)
                elif command == "ECHO":
                    message = elements[4].decode("utf-8")
                    resp = self.parse_request(message)
                    print(f"Response sent {resp}")
                    client_socket.sendall(resp)
                elif command == "SET":
                    key = elements[4].decode("utf-8")
                    value = elements[6].decode("utf-8")
                    expiration = None

                    if len(elements) > 8:
                        if elements[8] == b'ex':
                            expiration = int(elements[10].decode("utf-8")) * 1000
                        elif elements[8] == b'px':
                            expiration = int(elements[10])

                        print(f"Setting key '{key}' to value '{value}' with expiration of {expiration} ms")

                    self.store.set_elements(key, value, expiration / 1000 if expiration else None)
                    resp = self.parse_request("OK")
                    client_socket.sendall(resp)
                elif command == "GET":
                    key = elements[4].decode("utf-8")
                    print(f"Getting key {key}")

                    value = self.store.get_elements_by_key(key)
                    if value is not None:
                        resp = self.parse_request(value)
                        client_socket.sendall(resp)
                        print(f"Sending stored value {value}")
                    else:
                        print(f"Key '{key}' not found or expired, sending null bulk string")
                        resp = self.parse_request(b"$-1\r\n")
                        client_socket.sendall(resp)
                else:
                    print("Unsupported command")
                    error_resp = self.parse_request("ERROR Unsupported command")
                    client_socket.sendall(error_resp)
                    self.running = False

        except (ConnectionResetError, BrokenPipeError):
            print("Client disconnected")
        except OSError as e:
            print(f"OSError: {e}")
        finally:
            try:
               client_socket.close()
            except OSError as e:
                print(f"Error closing socket: {e}")
