# -*- coding: utf-8 -*-
"""
@author: bkc
"""


import logging

class KbicLogger(logging.getLoggerClass()):

    dft_level = logging.DEBUG
    logging.basicConfig(level = logging.DEBUG,
    format = '%(asctime)s %(module)-15s %(lineno)-4d %(threadName)s %(levelname)-8s %(message)s',
    datefmt = '%Y-%m-%d(%a)%H:%M:%S',
    filename = 'log.txt',
    filemode = 'w')
    def __init__(self, name=None, formatter=None, handler=None, level=None):

        if not name:
            name = 'root'
        super().__init__(name)

        if not handler:
            handler = logging.StreamHandler()
        if not formatter:
            formatter = logging.Formatter(
                '%(asctime)s %(module)-15s %(lineno)-4d %(threadName)s %(levelname)-8s %(message)s')
        if not level:
            level = self.dft_level
        handler.setFormatter(formatter)
        self.addHandler(handler)
        self.setLevel(level)

    @classmethod
    def set_defaultlevel(cls, level):

        dft_level = logging.INFO

        if level == 'NOTSET':
            dft_level = logging.NOTSET
        elif level == 'DEBUG':
            dft_level = logging.DEBUG
        elif level == 'INFO':
            dft_level = logging.INFO
        elif level == 'WARNING':
            dft_level = logging.WARNING
        elif level == 'ERROR':
            dft_level = logging.ERROR
        elif level == 'CRITICAL':
            dft_level = logging.CRITICAL
        else:
            pass # ignore
        
        cls.dft_level = dft_level

logger = KbicLogger()

def print_hex(data):
    l = [hex(int(i)) for i in data]
    print(" ".join(l))
    print("\r\n")
