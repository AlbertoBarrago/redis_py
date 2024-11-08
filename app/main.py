import argparse
import socket
import threading

from app.services.req_handler import RequestService
from app.store.global_store import GlobalStore

store = GlobalStore()

def perform_handshake(host, port):
    master_socket = socket.create_connection((host, port))
    master_socket.sendall(str.encode("*1\r\n$4\r\nping\r\n"))


def main():
    parser = argparse.ArgumentParser(description="Start a simple socket server.")
    parser.add_argument('--dir', type=str)
    parser.add_argument('--dbfilename', type=str)
    parser.add_argument('--port', type=int, default=6379, help="Porta su cui avviare il server Redis")
    parser.add_argument('--replicaof', type=str)
    args = parser.parse_args()

    if args.replicaof:
        host, port = args.replicaof.split()
        port = int(port)
        print(
            f"Waiting for handshake with master server {host}:{port}..."
        )
        perform_handshake(host, port)

    path = args.dir if args.dir else ""
    dbfilename = args.dbfilename if args.dbfilename else ""
    port = args.port

    replica = "master"
    if args.replicaof:
        replica = "slave"

    print(f"Server:{dbfilename} is running on port {port}")
    print(f"Replica is {replica}")
    print(f"Waiting for connections...")

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
