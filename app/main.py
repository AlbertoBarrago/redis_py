import argparse
import socket
import threading

from app.services.req_handler import RequestService
from app.store.global_store import GlobalStore

store = GlobalStore()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str)
    parser.add_argument('--dbfilename', type=str)
    parser.add_argument('--port', type=int, default=6379, help="Porta su cui avviare il server Redis")
    parser.add_argument('--replicaof', type=str)
    args = parser.parse_args()

    path = args.dir if args.dir else ""
    dbfilename = args.dbfilename if args.dbfilename else ""
    port = args.port
    replica = "master"
    if args.replicaof:
        replica = "slave"

    print(f"{args.replicaof}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", port))
    server_socket.listen()

    request_service = RequestService(store=store, dir_path=path, dbfilename=dbfilename, port=port, replica=replica)
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
