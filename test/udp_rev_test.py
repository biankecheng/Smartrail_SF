import socket

def receive_udp_message(address, port):
    """
    接收UDP数据

    :param address: 绑定的IP地址 (通常为 "0.0.0.0" 表示监听所有接口)
    :param port: 绑定的端口号
    """
    # 创建UDP套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # 绑定到指定的IP地址和端口号
        udp_socket.bind((address, port))
        print(f"正在监听 {address}:{port}...")

        while True:
            # 接收数据
            data, client_address = udp_socket.recvfrom(1024)  # 缓冲区大小为1024字节
            print(f"收到数据: {data.decode()}，来自: {client_address}")

            # 如果需要退出接收循环，可以在这里添加条件
            # 例如，收到特定消息时退出
            if data.decode() == "exit":
                print("收到退出指令，停止接收数据。")
                break

    except Exception as e:
        print(f"接收数据时出错: {e}")
    finally:
        # 关闭套接字
        udp_socket.close()
        print("UDP套接字已关闭")

# 示例用法
if __name__ == "__main__":
    address = "0.0.0.0"  # 监听所有接口
    port = 8888       # 监听的端口号
    receive_udp_message(address, port)