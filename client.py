import socket

def main():
    host = "127.0.0.1"
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print(sock.recv(1024).decode())  # Receive welcome message

        while True:
            answer = input("Enter your answer:")
            sock.sendall(answer.encode())

            response = sock.recv(1024).decode()
            print(response)

            if response.startswith("Game over"):
                break

if __name__ == "__main__":
    main()
