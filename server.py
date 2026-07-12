import socket
import threading
import sys

NAME_TAG = "__NAME__:"

def receive_messages(sock, peer_name, my_name):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nConnection closed by the other side.")
                sock.close()
                sys.exit(0)
            message = data.decode("utf-8")
            print(f"\r\033[2K{peer_name}: {message}\n{my_name}(You): ", end="", flush=True)
        except (ConnectionResetError, OSError):
            print("\nConnection lost.")
            sys.exit(0)


def send_messages(sock, my_name):
    while True:
        message = input(f"{my_name}(You): ")
        if message.lower() == "exit":
            sock.close()
            sys.exit(0)
        try:
            sock.sendall(message.encode("utf-8"))
        except OSError:
            print("Could not send message. Connection may be closed.")
            sys.exit(0)


def exchange_names(conn, my_name):
    conn.sendall((NAME_TAG + my_name).encode("utf-8"))
    data = conn.recv(1024).decode("utf-8")
    if data.startswith(NAME_TAG):
        return data[len(NAME_TAG):]
    return "Client"


def run_server(port, my_name):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", port))
    server_sock.listen(1)
    print(f"Waiting for a connection on port {port}...")

    conn, addr = server_sock.accept()
    print(f"Connected to {addr}.")

    peer_name = exchange_names(conn, my_name)
    print(f"Chatting with {peer_name}. Start chatting (type 'exit' to quit).\n")

    receiver = threading.Thread(target=receive_messages, args=(conn, peer_name, my_name), daemon=True)
    receiver.start()

    send_messages(conn, my_name)


def main():
    my_name = input("Enter your username: ").strip() or "Server"

    port_input = input("Enter port to listen on (default 5000): ").strip()
    port = int(port_input) if port_input else 5000

    run_server(port, my_name)


if __name__ == "__main__":
    main()