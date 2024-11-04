class RequestService:
    def __init__(self, data=None, encoding="utf-8", store=None):
        self.data = data
        self.encoding = encoding
        self.running = True
        self.store = store

    def parse_request(self, data):
        separator = "\r\n"
        if isinstance(data, str):
            return f"+{data}{separator}".encode(self.encoding)
        elif isinstance(data, bytes):
            return data
        else:
            # Assume data is an integer for bulk strings
            return f"${len(data)}{separator}{data}{separator}".encode(self.encoding)

    def handle_client(self, client_socket):
        try:
            while self.running:
                self.data = client_socket.recv(1024)

                if not self.data:
                    break

                print("Received {!r}".format(self.data))
                elements = [el for el in self.data.split(b"\r\n") if el]
                if len(elements) < 2:
                    continue

                command = elements[1].decode('utf-8').upper()
                print(f"Command: {command}")

                if command == "PING":
                    resp = self.parse_request("PONG")
                    print(f"Sending PONG response -> {resp}")
                    client_socket.sendall(resp)
                elif command == "ECHO":
                    if len(elements) < 3:
                        error_resp = self.parse_request("ERROR Missing argument for ECHO")
                        client_socket.sendall(error_resp)
                        continue
                    message = elements[2].decode("utf-8")
                    resp = self.parse_request(message)
                    print(f"Response sent {resp}")
                    client_socket.sendall(resp)
                elif command == "SET":
                    if len(elements) < 4:
                        error_resp = self.parse_request("ERROR Missing key/value for SET")
                        client_socket.sendall(error_resp)
                        continue
                    key = elements[2].decode("utf-8")
                    value = elements[3].decode("utf-8")
                    expiration = None
                    if len(elements) > 4:
                        if elements[4].lower() == b'ex':
                            expiration = int(elements[5].decode("utf-8")) * 1000
                        elif elements[4].lower() == b'px':
                            expiration = int(elements[5].decode("utf-8"))

                    self.store.set_elements(key, value, expiration / 1000 if expiration else None)
                    resp = self.parse_request("OK")
                    client_socket.sendall(resp)
                elif command == "GET":
                    key = elements[2].decode("utf-8")
                    print(f"Getting key {key}")
                    value = self.store.get_elements_by_key(key)
                    if value is not None:
                        resp = self.parse_request(value)
                        client_socket.sendall(resp)
                        print(f"Sending stored value {value}")
                    else:
                        resp = self.parse_request(b"$-1\r\n")
                        client_socket.sendall(resp)
                        print(f"Key '{key}' not found or expired, sending null bulk string")
                else:
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
