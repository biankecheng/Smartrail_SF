"""
@author: bkc
"""
from TRDP import trdp

def main(queue):
    # ip = '10.0.12.140'
    ip = "239.255.14.8"
    comid = 2438
    # ip = "239.255.14.1"
    # comid = 2430
    trdp_link = trdp(ip,comid)
    print('TRDP已加入组播')
    while True:
        try:
          data = trdp_link.trdp_rev()
          print("数据长度为：{}".format(len(data)))
        except Exception as e :
           print(e)
        else:
          queue.put(data)
          print("数据已存入队列")