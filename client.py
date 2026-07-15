import socket
import threading
import sys

NAME_TAG = "__NAME__:"

def receive_messages(sock, my_name):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nDisconnected from server.")
                break

            print(f"\r\033[2K{data.decode('utf-8')}")
            print(f"{my_name}: ", end="", flush=True)

        except:
            break


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
    return "Server"


def run_client(host, port, my_name):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to {host}:{port}...")
    client_sock.connect((host, port))
    print("Connected.")

    peer_name = exchange_names(client_sock, my_name)
    print("Connected to chat server.")
    print("Type 'exit' to quit.\n")

    receiver = threading.Thread(
        target=receive_messages,
        args=(client_sock, my_name),
        daemon=True
    )   
    receiver.start()
    try:
        send_messages(client_sock, my_name)
    except KeyboardInterrupt:
        print("\nLeaving chat...")
        client_sock.close()


def main():
    my_name = input("Enter your username: ").strip() or "Client"

    host_input = input("Enter server host/IP (default 127.0.0.1): ").strip()
    host = host_input if host_input else "127.0.0.1"

    port_input = input("Enter server port (default 5000): ").strip()
    port = int(port_input) if port_input else 5000

    run_client(host, port, my_name)


if __name__ == "__main__":
    main()