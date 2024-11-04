import socket  # noqa: F401
import threading  # noqa: F401


def handle_client(client_socket):
    try:
        while True:
            request = client_socket.recv(1024).decode("utf-8")
            if not request:
                break
            print(f"Received request: {request}")
            response = "+PONG\r\n"
            client_socket.sendall(response.encode("utf-8"))
            print(f"Sent response: {response}")
    except ConnectionResetError:
        print("Client disconnected")
    finally:
        client_socket.close()

def main():
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
