""" Redi from scratch -> https://app.codecrafters.io/ """
import socket  # noqa: F401
import threading  # noqa: F401


def parse_request(data, encoding="utf-8"):
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
    while True:
        data = client_socket.recv(32)

        if not data:
            break

        print("Received {!r}".format(data))
        arr_size, *arr = data.split(b"\r\n")
        print(f"Array size: {arr_size}")
        print(f"Array content: {arr}")

        if arr[1] == b"ping":
            resp = parse_request("PONG")
            print(f"Sending PONG reps ->, {resp}")
            print(f"Response sent {resp}")
            client_socket.sendAll(resp)
        elif arr[1] == b"echo":
            resp = parse_request([el.decode("utf-8") for el in arr[3::2]])
            print(f"Response sent {resp}")
            client_socket.sendAll(resp)
        else:
            break
        client_socket.close()


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
