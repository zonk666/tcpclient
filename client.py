import socket
import random
import sys

def send_initialization(sock, num_blocks):
    message = b'\x01\x00' + num_blocks.to_bytes(4, byteorder='big')
    sock.sendall(message)
    print(f"发送初始化消息，块数: {num_blocks}")

def send_reverse_request(sock, data):
    length = len(data)
    message = b'\x03\x00' + length.to_bytes(4, byteorder='big') + data.encode('ascii')
    sock.sendall(message)
    print(f"发送反转请求，数据: {data}")

def receive_reverse_answer(sock):
    header = sock.recv(6)
    if len(header) < 6:
        raise ConnectionError("收到不完整的头部")
    length = int.from_bytes(header[2:], byteorder='big')
    reversed_data = sock.recv(length).decode('ascii')
    print(f"收到反转数据: {reversed_data}")
    return reversed_data

def main(server_ip, server_port, lmin, lmax):
    # 读取ASCII文件
    try:
        with open("ascii_file.txt", "r") as f:
            data = f.read()
    except FileNotFoundError:
        print("未找到ASCII文件")
        return

    if not data:
        print("ASCII文件为空")
        return

    # 随机划分数据块
    blocks = []
    start = 0
    while start < len(data):
        length = random.randint(lmin, lmax)
        blocks.append(data[start:start + length])
        start += length

    num_blocks = len(blocks)
    print(f"总块数: {num_blocks}")

    # 连接服务器
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        print(f"连接到服务器 {server_ip}:{server_port}")

        # 发送初始化报文
        send_initialization(sock, num_blocks)

        # 接收服务器的同意报文
        agreement = sock.recv(2)
        if agreement != b'\x02\x00':
            raise ConnectionError("服务器未发送同意消息")
        print("收到服务器同意消息")

        # 逐块发送反转请求报文并接收反转应答报文
        reversed_data_blocks = []
        for i, block in enumerate(blocks):
            send_reverse_request(sock, block)
            reversed_block = receive_reverse_answer(sock)
            print(f"第{i+1}块: {reversed_block}")
            reversed_data_blocks.append(reversed_block)

        # 将反转后的数据块拼接并保存到文件
        reversed_data = ''.join(reversed_data_blocks)
        with open("reversed_ascii_file.txt", "w") as f:
            f.write(reversed_data)
        print("反转后的数据已保存到 reversed_ascii_file.txt")

if __name__ == "__main__":
    # 默认值
    default_server_ip = "127.0.0.1"
    default_server_port = 8080
    default_lmin = 10
    default_lmax = 20

    if len(sys.argv) != 5:
        print("使用默认值:")
        print(f"服务器IP: {default_server_ip}")
        print(f"服务器端口: {default_server_port}")
        print(f"最小块长度: {default_lmin}, 最大块长度: {default_lmax}")
        server_ip = default_server_ip
        server_port = default_server_port
        lmin = default_lmin
        lmax = default_lmax
    else:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        lmin = int(sys.argv[3])
        lmax = int(sys.argv[4])

    main(server_ip, server_port, lmin, lmax)
