# -*- coding: utf-8 -*-
"""
@author: BKC
"""
import struct as st
from ctypes import create_string_buffer
import datetime
from kbic_logging import logger

class MetaCell():
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length


METADATAFORMAT = {
    'MDCU1': MetaCell(0, 16),
    'MDCU2': MetaCell(17, 16),
    'MDCU3': MetaCell(33, 16),
    'MDCU4': MetaCell(39, 16),
}

METADATAFORMAT1 = {
    'MDCU4': MetaCell(0, 16),
    'MDCU3': MetaCell(17, 16),
    'MDCU2': MetaCell(33, 16),
    'MDCU1': MetaCell(39, 16),
}

DOORWARNDATA = {
    'D1': MetaCell(0, 4),
    'D2': MetaCell(4, 4),
    'D3': MetaCell(8, 4),
    'D4': MetaCell(12, 4),
}


LifeSign = 0x0000

def handle_lifeSign():
    global LifeSign
    LifeSign = LifeSign + 1
    if LifeSign >= 0xffff:
        LifeSign = 0
    return LifeSign


def pack_head():
    signal = create_string_buffer(17)
    LifeSign = handle_lifeSign()
    signal[0] = 0xAA
    signal[1] = 0x61
    st.pack_into('>H', signal, 2, 363)
    signal[4] = 0x00
    signal[5] = 0x05
    signal[6] = 0x04
    signal[7] = 0x00
    signal[8] = 0x00
    st.pack_into('>H', signal, 9, LifeSign)
    curr_time = datetime.datetime.now()
    signal[11] = curr_time.year - 2000
    signal[12] = curr_time.month
    signal[13] = curr_time.day
    signal[14] = curr_time.hour
    signal[15] = curr_time.minute
    signal[16] = curr_time.second
    return signal


def handle_warnDoor(obj):
    data = create_string_buffer(4)
    tmp = 0x00
    tmp = (obj.get('AuxLockLoAbnormal', 0) << 7)
    tmp = ((obj.get('AuxLockUnloAbnormal', 0) << 6) | tmp)
    tmp = ((obj.get('ClosedSwAbnormal', 0) << 5) | tmp)
    tmp = ((obj.get('ClCurrentOver', 0) << 4) | tmp)
    tmp = ((obj.get('OpTimeOver', 0) << 3) | tmp)
    tmp = ((obj.get('ClTimeOver', 0) << 2) | tmp)
    tmp = ((obj.get('OpCurrentOver', 0) << 1) | tmp)
    tmp = (obj.get('CloseCurrAbnormal', 0) | tmp)
    data[0] = tmp
    tmp = 0x00
    tmp = (obj.get('OpSealAdhesionAbnormal', 0) << 3)
    tmp = ((obj.get('PositionAbnormal', 0) << 2) | tmp)
    tmp = ((obj.get('ClCresistanceOver', 0) << 1) | tmp)
    tmp = (obj.get('OpCresistanceOver', 0) | tmp)
    data[2] = tmp
    return data


def handle_warnData(msg,unit):
    warnData = create_string_buffer(64)
    if unit in (6,5):
        for key in METADATAFORMAT.keys():
            obyte = METADATAFORMAT[key].offset
            size = METADATAFORMAT[key].length
            warn = msg.get(key, {})
            door_warn = create_string_buffer(16)
            for key1 in DOORWARNDATA.keys():
                door_obyte = DOORWARNDATA[key1].offset
                door_size = DOORWARNDATA[key1].length
                door_warn[door_obyte:door_obyte+door_size] = handle_warnDoor(warn[key1])
            warnData[obyte:obyte+size] =door_warn
    else:
        for key in METADATAFORMAT1.keys():
            obyte = METADATAFORMAT1[key].offset
            size = METADATAFORMAT1[key].length
            warn = msg.get(key, {})
            door_warn = create_string_buffer(16)
            for key1 in DOORWARNDATA.keys():
                door_obyte = DOORWARNDATA[key1].offset
                door_size = DOORWARNDATA[key1].length
                door_warn[door_obyte:door_obyte+door_size] = handle_warnDoor(warn[key1])
            warnData[obyte:obyte+size] =door_warn
    return warnData

def cal_crc(data, l):
    b = 0
    crc = 0xFFFF
    i = 0
    j = 0
    for i in data:
        for j in range(0, 8):
            b = (((i << j) & 0x80) ^ ((crc & 0x8000) >> 8))
            crc = crc << 1
            crc = (crc & 0xffff)
            if b != 0:
                crc = crc ^ 0x1021
    return crc

def pack_msg(msg):
    signal = create_string_buffer(500)
    unit = msg['Unit']
    warn_data = handle_warnData(msg,unit)
    signal[0:17] = pack_head()
    if unit  == 6:
        signal[17:81] =warn_data
    elif  unit == 9:
        signal[81:145] = warn_data
    elif  unit == 5:
        signal[217:281] = warn_data
    elif  unit == 10:
        signal[281:345] = warn_data
    crc = cal_crc(signal[0:498],498)
    st.pack_into('>H',signal,498,crc)
    signal = bytes(signal)
    return signal

def pack_lifedata():
    signal = create_string_buffer(30)
    LifeSign = handle_lifeSign()
    signal[0] = 0xAA
    signal[1] = 0x60
    st.pack_into('>H',signal,2,30)
    signal[4] = 0x01
    signal[5] = 0x01
    signal[6] = 0x04
    signal[7] = 0x00
    signal[8] = 0x00
    st.pack_into('>H',signal,9,LifeSign)
    curr_time = datetime.datetime.now()
    signal[11] = curr_time.year - 2000
    signal[12] = curr_time.month
    signal[13] = curr_time.day
    signal[14] = curr_time.hour
    signal[15] = curr_time.minute
    signal[16] = curr_time.second
    signal[17] = 0x01
    signal[18] = 0x01
    st.pack_into('>H',signal,19,LifeSign)
    crc = cal_crc(signal[0:28],28)
    st.pack_into('>H',signal,28,crc)
    signal = bytes(signal)
    return signal

if __name__ == "__main__":

    data = {'Unit': 6, 'MDCU1': {'D1': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 1, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D2': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D3': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D4': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}}, 'MDCU2': {'D1': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D2': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D3': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D4': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}}, 'MDCU3': {'D1': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D2': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D3': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D4': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}}, 'MDCU4': {'D1': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D2': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D3': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}, 'D4': {'AuxLockLoAbnormal': 1, 'AuxLockUnloAbnormal': 0, 'ClosedSwAbnormal': 0, 'ClCurrentOver': 0, 'OpCurrentOver': 0, 'ClTimeOver': 0, 'OpTimeOver': 0, 'OpSealAdhesionAbnormal': 0, 'PositionAbnormal': 0, 'ClCresistanceOver': 0, 'OpCresistanceOver': 0}}}
    msg = pack_msg(data)
    print(msg)
    life = pack_lifedata()
    print(life)