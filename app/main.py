import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    try:
        client, addr = server_socket.accept() # wait for client
        print(f"Connected to {addr}")
        request = client.recv(1024).decode("utf-8")
        print(f"Received request {request}")
        response = "+PONG\r\n"
        client.sendall(response.encode("utf-8"))
        print(f"Sent response {response}")
        client.close()
    except KeyboardInterrupt:
        print("Shutting down server")
    finally:
        server_socket.close()



if __name__ == "__main__":
    main()
