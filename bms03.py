#!/usr/bin/env python3
import asyncio

from influxdb import InfluxDBClient

#bluetoothctl --timeout 3 scan on && ./bmslog.py A4:C1:37:11:8A:FF
from smart_bms.SmartBMSClient import SmartBMSClient
from smart_bms.TransportBLE import TransportBLE
from db import db
def isValid(data):
    if data['Ibat'] > 150:
        return False
    if data['Vbat'] < 6 or data['Vbat'] > 18:
        return False
    for i in range(1,5):
        if data['V{0:0=2}'.format(i)] < 2 or data['V{0:0=2}'.format(i)] > 4:
            return False
    return True

def bal2int(inp):
    out = 0

    return out
    

async def main():
    tr = TransportBLE("A4:C1:37:11:8A:FF")
    await tr.start()
    rawdat={}
    client = SmartBMSClient(tr)

    while True:
        try:
            basic_info = await client.read_basic_information()
            print(basic_info)
            rawdat['Vbat']=basic_info.voltage/1000
            rawdat['Ibat']=basic_info.current/1000
            rawdat['CapRem']=basic_info.remaining_capacity/1000
            rawdat['Cap']=basic_info.nominal_capacity/1000
            rawdat['Ncycles']=basic_info.cycles
            rawdat['Bal']=bal2int(basic_info.cell_balancing_status)
            rawdat['T1']=basic_info.temperatures[0]
            rawdat['T2']=basic_info.temperatures[1]
            cell_voltages = await client.read_cell_voltages()
            print(cell_voltages)
            rawdat['V01']=cell_voltages[0]/1000
            rawdat['V02']=cell_voltages[1]/1000
            rawdat['V03']=cell_voltages[2]/1000
            rawdat['V04']=cell_voltages[3]/1000
            if isValid(rawdat):
                db.dbsave('bms03', rawdat)

            #await asyncio.sleep(1)
            break
        except asyncio.exceptions.TimeoutError:
            print("timeout")
            await asyncio.sleep(1)


asyncio.run(main())
