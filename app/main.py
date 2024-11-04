import socket
import threading

from app.services.request_service import RequestService
from app.store.global_store import GlobalStore

store = GlobalStore()

def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    request_service = RequestService(store=store)
    print("Server started on localhost:6379")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected to {addr}")
            threading.Thread(target=request_service.handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        print("Shutting down server")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
