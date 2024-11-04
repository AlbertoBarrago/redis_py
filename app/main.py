import socket
import threading
import time

from app.global_store import GlobalStore

# Global store for key-value pairs and their expiration times
store = GlobalStore()

def parse_request(data, encoding="utf-8"):
    separator = "\r\n"
    encoded = f"+{data}{separator}"
    print(f"encoded: {encoded}")
    return encoded.encode(encoding=encoding)

def handle_client(client_socket):
    running = True
    try:
        while running:
            data = client_socket.recv(1024)

            if not data:
                break

            print("Received {!r}".format(data))
            elements = [el for el in data.split(b"\r\n") if el]
            if not elements:
                continue

            print(f"Elements: {elements}")

            command = elements[2].decode('utf-8')
            print(f"Command: {command}")

            if command == "PING":
                resp = parse_request("PONG")
                print(f"Sending PONG response -> {resp}")
                client_socket.sendall(resp)
            elif command == "ECHO":
                message = elements[4].decode("utf-8")
                resp = parse_request(message)
                print(f"Response sent {resp}")
                client_socket.sendall(resp)
            elif command == "SET":
                key = elements[4].decode("utf-8")
                value = elements[6].decode("utf-8")
                if len(elements) > 8 and elements[8] == b'EX':
                    expiration = int(elements[9].decode("utf-8"))
                    print(f"Setting key {key} to value {value} with expiration of {expiration} seconds")
                    expiration_time = time.time() + expiration
                else:
                    print(f"Setting key {key} to value {value} without expiration")
                    expiration_time = None

                store.set_elements(value, expiration_time)
                resp = parse_request("OK")
                client_socket.sendall(resp)
            elif command == "GET":
                key = elements[4].decode("utf-8")
                print(f"Getting key {key}")

                value = store.get_elements_by_key(key)
                if value is not None:
                    resp = parse_request(value)
                    print(f"Sending stored value {value}")
                else:
                    resp = parse_request("null bulk string")
                client_socket.sendall(resp)
            else:
                print("Unsupported command")
                error_resp = parse_request("ERROR Unsupported command")
                client_socket.sendall(error_resp)
                running = False

    except (ConnectionResetError, BrokenPipeError):
        print("Client disconnected")
    except OSError as e:
        print(f"OSError: {e}")
    finally:
        try:
            client_socket.close()
        except OSError as e:
            print(f"Error closing socket: {e}")

def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Server started on localhost:6379")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected to {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("Shutting down server")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
