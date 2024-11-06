import argparse
import socket
import threading

from app.services.req_handler import RequestService
from app.store.global_store import GlobalStore

store = GlobalStore()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", 6379))
    server_socket.listen()

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str)
    parser.add_argument('--dbfilename', type=str)
    args = parser.parse_args()
    path = args.dir if args.dir else ""
    dbfilename = args.dbfilename if args.dbfilename else ""
    request_service = RequestService(store=store, dir_path=path, dbfilename=dbfilename)
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
