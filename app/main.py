""" Redi from scratch -> https://app.codecrafters.io/ """
import socket  # noqa: F401
import threading  # noqa: F401
from urllib.parse import urlparse, parse_qs  # noqa: F401


def parse_request(request: str):
    lines = request.split('\r\n')

    if len(lines) < 5:
        raise ValueError('Invalid request format: insufficient lines')

    try:
        if lines[0] != '*2':
            raise ValueError('Invalid request format: incorrect command count prefix')

        command = str(lines[2])

        if not lines[4]:
            raise ValueError('Invalid argument length prefix')
        argument_length = len(lines[4])

        argument = lines[4]
        if len(argument) != argument_length:
            raise ValueError('Invalid argument length')

        return command, argument

    except (IndexError, ValueError) as e:
        raise ValueError(f'Invalid request format: {e}') from e


def handle_client(client_socket):
    """
    Handle client request, parsing response and sending it back.
    :param client_socket:
    :return:
    """
    try:
        while True:
            request = client_socket.recv(1024).decode("utf-8")

            if not request:
                break
            # print(f"Received request: {request}")

            command, args = parse_request(request)
            print(f"Received request: {command}, args: {args}")

            response = "-Error: Unsupported command\r\n"
            if command == 'ECHO':
                response = f"${len(command)}\r\n{command}\r\n"
            elif command == 'PING':
                response = "+PONG\r\n"


            client_socket.sendall(response.encode("utf-8"))
            print(f"Sent response: {response}")
    except ConnectionResetError:
        print("Client disconnected")
    finally:
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
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down server")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
