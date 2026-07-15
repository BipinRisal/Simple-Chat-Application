import socket
import threading

HOST = "0.0.0.0"
PORT = 5000
NAME_TAG = "__NAME__:"

clients = []
client_names = {}
lock = threading.Lock()


def broadcast(message, sender=None):
    with lock:
        disconnected = []

        for client in clients:
            if client != sender:
                try:
                    client.sendall(message.encode("utf-8"))
                except:
                    disconnected.append(client)

        for client in disconnected:
            clients.remove(client)
            client.close()


def handle_client(conn, addr):
    try:
        # Receive username
        data = conn.recv(1024).decode("utf-8")

        if data.startswith(NAME_TAG):
            name = data[len(NAME_TAG):]
        else:
            name = f"{addr[0]}:{addr[1]}"

        # Send server name back
        conn.sendall((NAME_TAG + "Server").encode("utf-8"))

        with lock:
            clients.append(conn)
            client_names[conn] = name

        print(f"{name} connected.")

        broadcast(f"*** {name} joined the chat ***", conn)

        while True:
            data = conn.recv(1024)

            if not data:
                break

            message = data.decode("utf-8")
            print(f"{name}: {message}")

            broadcast(f"{name}: {message}", conn)

    except:
        pass

    finally:
        with lock:
            if conn in clients:
                clients.remove(conn)

            name = client_names.pop(conn, "Unknown")

        conn.close()

        print(f"{name} disconnected.")
        broadcast(f"*** {name} left the chat ***")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()

    print(f"Server listening on port {PORT}")

    while True:
        conn, addr = server.accept()

        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    main()