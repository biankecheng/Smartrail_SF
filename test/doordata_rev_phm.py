import socket
import struct
import select
from multiprocessing import Queue
# from V02.door_decode import decode_msg


def sock_rev_test(mcast_grp, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mreq = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    return sock


def main():
    # 门控器PHM数据
    door_ip = '239.255.14.8'
    # door_ip = '239.255.14.1'
    door_port = 17224
    door_data = sock_rev_test(door_ip, door_port)
    with open('2438.bin','wb') as s:
        while True:
            try:
                data, address = door_data.recvfrom(2048)
                s.write(data)
                print("源ip为：{}".format(address))
                print(data)
            except Exception as e:
                print(e)
        # else:
        #     queue_door = Queue() 
        #     queue_door.put(data)

        # try:
        #     while not queue_door.empty():
        #         data = queue_door.get()
        #         comid = int.from_bytes(data[11:13], byteorder='big', signed=True)
        #         if comid == 2565:
        #             phm_alert = decode_msg(data)

        # except Exception as e:
        #     print(e)


if __name__ == '__main__':
    main()
