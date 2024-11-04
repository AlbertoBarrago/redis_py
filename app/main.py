""" Redi from scratch -> https://app.codecrafters.io/ """
import socket  # noqa: F401
import threading  # noqa: F401


def parse_request(data, encoding="utf-8"):
    """
     Doc -> https://redis.io/docs/latest/develop/reference/protocol-spec/#bulk-strings
    :param data:
    :param encoding:
    :return:
    """
    if not isinstance(data, list):
        data = [data]

    separator = "\r\n"
    size = len(data)
    encoded = []

    for args in data:
        encoded.append(f"${len(args)}")
        encoded.append(args)
    if size > 1:
        encoded.insert(0, f"*{size}")

    print(f"encoded: {encoded}")
    return (separator.join(encoded) + separator).encode(encoding=encoding)


def handle_client(client_socket):
    """
    Handle client request, parsing response and sending it back.
    :param client_socket:
    :return:
    """
    running = True
    try:
        while running:
            data = client_socket.recv(32)

            if not data:
                break

            print("Received {!r}".format(data))
            arr_size, *arr = [el for el in data.split(b"\r\n") if el]
            if not arr:
                continue
            print(f"Array size: {arr_size}")
            print(f"Array content: {arr}")

            if arr[0] == b"PING":
                resp = parse_request("PONG")
                print(f"Sending PONG response -> {resp}")
                client_socket.sendall(resp)
            elif arr[0] == b"ECHO":
                resp = parse_request([el.decode("utf-8") for el in arr[1:]])
                print(f"Response sent {resp}")
                client_socket.sendall(resp)
            else:
                print("Unsupported command")
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
    """
    Main function
    :return:
    """
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