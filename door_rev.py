# -*- coding: utf-8 -*-
"""
@author: bkc
"""
import socket
import struct
from kbic_logging import logger

def udp_multicast_receiver(multicast_group, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    return sock

def main(queue):
    ip = "239.193.0.132"
    port = 3122
    sock = udp_multicast_receiver(ip, port)
    while True:
        try:
          data = sock.recv(1024)
          # print("数据长度为：{}".format(len(data)))
        except Exception as e :
           logger.error(e)
        else:
          queue.put(data)
          print("数据已存入队列")