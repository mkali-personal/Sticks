import socket

UDP_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", UDP_PORT))

print(f"Listening for UDP logs on port {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(1024)
    print(data.decode().strip())
