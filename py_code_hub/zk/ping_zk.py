import socket

# Bind to all IPv4 interfaces
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", 8000))
server_socket.listen(5)

print("Listening for raw hardware packets on port 8000...")

while True:
    client, addr = server_socket.accept()
    print(f"\n[+] CONNECTION RECEIVED FROM: {addr[0]}:{addr[1]}")
    data = client.recv(1024)
    print(f"Data:\n{data.decode('utf-8', errors='ignore')}")
    client.sendall(
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK"
    )
    client.close()