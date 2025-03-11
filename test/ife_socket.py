import socket
import struct

# udp组播接受trdp组播数据
def trdp_zb_sock(mcast_grp, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mreq = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    return sock

# udp单播
def udp_socket(mcast_grp, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((mcast_grp, port))
    return sock

    