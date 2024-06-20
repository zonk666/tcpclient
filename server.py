import socket
import threading
import sys

def handle_client(conn):
    try:
        # 接收Initialization报文
        header = conn.recv(6)
        if header[:2] != b'\x01\x00':
            raise ValueError("Invalid initialization message")
        num_blocks = int.from_bytes(header[2:], byteorder='big')

        # 发送Agreement报文
        conn.sendall(b'\x02\x00')

        # 处理每个reverseRequest报文并发送reverseAnswer报文
        for _ in range(num_blocks):
            header = conn.recv(6)
            if header[:2] != b'\x03\x00':
                raise ValueError("Invalid reverse request message")
            length = int.from_bytes(header[2:], byteorder='big')
            data = conn.recv(length).decode('ascii')
            reversed_data = data[::-1]
            response = b'\x04\x00' + len(reversed_data).to_bytes(4, byteorder='big') + reversed_data.encode('ascii')
            conn.sendall(response)
    finally:
        conn.close()

def main(server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((server_ip, server_port))
        sock.listen()

        print(f"Server listening on {server_ip}:{server_port}")

        while True:
            conn, addr = sock.accept()
            print(f"Connected by {addr}")
            threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    # 默认值
    default_server_ip = "127.0.0.1"
    default_server_port = 8080

    if len(sys.argv) < 3:
        print("Usage: python server.py <server_ip> <server_port>")
        print(f"Using default values: {default_server_ip} {default_server_port}")
        server_ip = default_server_ip
        server_port = default_server_port
    else:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])

    main(server_ip, server_port)
