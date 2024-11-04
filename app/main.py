""" Redi from scratch -> https://app.codecrafters.io/ """
import socket
import threading


def parse_request(data, encoding="utf-8"):
    separator = "\r\n"
    # Simple String response should start with "+"
    encoded = f"+{data}{separator}"
    print(f"encoded: {encoded}")
    return encoded.encode(encoding=encoding)


def handle_client(client_socket):
    """
    Handle client request, parsing response and sending it back.
    :param client_socket:
    :return:
    """
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

            command = elements[1].decode('utf-8')
            print(f"Command: {command}")

            if command == "PING":
                resp = parse_request("PONG")
                print(f"Sending PONG response -> {resp}")
                client_socket.sendall(resp)
            elif command == "ECHO":
                # Decodifica e prepara i dati per l'eco
                message = elements[3].decode("utf-8")
                resp = parse_request(message)
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