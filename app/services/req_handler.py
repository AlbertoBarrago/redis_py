import time


class RequestService:
    """
     Request handling service
     :param data - incoming data
     :param store - store object
     :param dir_path - rdb path
     :param dbfilename - rdb filename
    """
    def __init__(self, data=None, encoding="utf-8", store=None, dir_path=None, dbfilename=None, port=None, replica=None):
        self.data = data
        self.encoding = encoding
        self.running = True
        self.store = store
        self.config = {
            "dir": dir_path,
            "dbfilename": dbfilename,
        }
        self.port = port
        self.replica = replica

    def parse_request(self, data):
        separator = "\r\n"
        if isinstance(data, str):
            return f"+{data}{separator}".encode(self.encoding)
        elif isinstance(data, bytes):
            return data
        else:
            return f"${len(data)}{separator}{data}{separator}".encode(self.encoding)

    def parse_bulk_string(self, message):
        return f"${len(message)}\r\n{message}\r\n".encode(self.encoding)

    def parse_array(self, items):
        response = f"*{len(items)}\r\n".encode(self.encoding)
        for item in items:
            response += self.parse_bulk_string(item)
        return response

    def parse_resp_array(self, data):
        elements = []
        if data[0] == ord('*'):
            lines = data.split(b'\r\n')
            num_elements = int(lines[0][1:])
            i = 1
            while i < len(lines) and len(elements) < num_elements:
                if lines[i] and lines[i][0] == ord('$'):
                    int(lines[i][1:])
                    i += 1
                    elements.append(lines[i].decode(self.encoding))
                i += 1
        return elements

    def handle_info_command(self, section):
        if section == "replication":
            info = "# Replication\r\n"
            info += f"role:{self.replica}\r\n"
            info += "connected_slaves:0\r\n"
            info += "master_replid:8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb\r\n"
            info += "master_repl_offset:0\r\n"
            info += "second_repl_offset:-1\r\n"
            info += "repl_backlog_active:0\r\n"
            info += "repl_backlog_size:1048576\r\n"
            info += "repl_backlog_first_byte_offset:0\r\n"
            info += "repl_backlog_histlen:0\r\n"
            bulk_string = f"${len(info)}\r\n{info}\r\n"
            return bulk_string
        return ""

    def handle_client(self, client_socket):
        try:
            while self.running:
                self.data = client_socket.recv(1024)

                if not self.data:
                    break

                #print("Received {!r}".format(self.data))
                elements = self.parse_resp_array(self.data)
                #print(f"Elements: {elements}")

                command = elements[0].upper()
                #print(f"Command: {command}")

                if command == "PING" or elements == "[PING]":
                    resp = self.parse_request("PONG")
                    #print(f"Sending PONG response -> {resp}")
                    client_socket.sendall(resp)

                if self.config.get('dir')  is not None or self.config.get('dbfilename') is not None:
                    self.store.load_rdb_file(
                        self.config.get('dir'),
                        self.config.get('dbfilename')
                    )

                match command:
                    case "ECHO":
                        message = elements[1]
                        resp = self.parse_request(message)
                        print(f"Response sent {resp}")
                        client_socket.sendall(resp)
                    case "SET":
                        key = elements[1]
                        value = elements[2]
                        expiration = None
                        if len(elements) > 4:
                            if elements[3].lower() == 'ex':
                                expiration = int(elements[4]) * 1000
                            elif elements[3].lower() == 'px':
                                expiration = int(elements[4]) + int(time.time() * 1000)
                        print(f"Setting key {key} with value {value} and expiration {expiration}")

                        self.store.set_elements(key, value, expiration if expiration else None)
                        resp = self.parse_request("OK")
                        client_socket.sendall(resp)
                    case "GET":
                        key = elements[1]
                        print(f"Getting key {key}")
                        value = self.store.get_elements_by_key(key)
                        if value is not None:
                            resp = self.parse_request(value)
                            client_socket.sendall(resp)
                            print(f"Sending stored value {value}")
                        else:
                            print(f"Key '{key}' not found, sending null bulk string")
                            resp = b"$-1\r\n"
                            print(f"sending this resp {resp}")
                            client_socket.sendall(resp)
                    case "CONFIG":
                        config_param = elements[2].lower()
                        if config_param == "dir":
                            response = self.parse_array([config_param, self.config.get('dir')])
                        elif config_param == "dbfilename":
                            response = self.parse_array(
                                [config_param, self.config.get('dbfilename')])
                        else:
                            response = b"*0\r\n"
                        client_socket.sendall(response)
                    case "KEYS":
                        arg = elements[1]
                        if arg == "*":
                            keys = self.store.get_all_keys()
                            response = self.parse_array(keys)
                            client_socket.sendall(response)
                    case "INFO":
                        arg = elements[1]
                        section = arg if len(arg) > 1 else ""
                        response = self.handle_info_command(section)
                        client_socket.sendall(response.encode(self.encoding))
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
