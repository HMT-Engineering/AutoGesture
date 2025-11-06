# Bluetooth LE scanner
# Prints the name and address of every nearby Bluetooth LE device

import asyncio
import time
import sys
from typing import Callable
from bleak import BleakClient, BleakScanner, BleakGATTCharacteristic

async def searchForWatch():
    print("Searching for watch")
    devices = await BleakScanner.discover()
    possibleDevice = None
    for device in devices:
        if(device.name and ("Watch" in device.name)):
            possibleDevice = device
    return possibleDevice

async def connectToWatch(mac):
    print(f"Connecting to {mac}")
    client =  BleakClient(mac)
    await client.connect()
    client.mtu_size
    return client  


async def disconnectFromWatch(client: BleakClient):
    await client.disconnect()

async def startRecording(client : BleakClient, timestamp: str):
    print("Starting recording")
    service = client.services.get_service("35CC4AB1-331F-48CC-82E2-D59EDEF46B0C")
    characteristic = service.get_characteristic("BBE236E7-7B70-4006-896E-9C596FB43CEA")
    await client.write_gatt_char(characteristic,("START:"+ timestamp).encode('utf-8'))

async def stopRecording(client : BleakClient, timestamp: str):
    service = client.services.get_service("35CC4AB1-331F-48CC-82E2-D59EDEF46B0C")
    characteristic = service.get_characteristic("BBE236E7-7B70-4006-896E-9C596FB43CEA")
    await client.write_gatt_char(characteristic, ("STOP:"+ timestamp).encode('utf-8'))

async def subscribeToData(client: BleakClient, callback: Callable[[BleakGATTCharacteristic, bytearray], None]):
    print("Subscribing to data")
    service = client.services.get_service("7BF01BA4-71E8-4B84-9617-ED4BC66E79D7")
    characteristic = service.get_characteristic("A5F9F023-A221-444A-886A-D26701087D40")
    await client.start_notify(characteristic, callback)

def dataProcessor(sender: BleakGATTCharacteristic, data: bytearray):
    dataString = data.decode('utf-8')
    messageParts = dataString.split("_")
    if(len(messageParts) != 2):
        print("Invalid message")
        return
    print(messageParts[0])
    # dataParts = messageParts[1].split(";")
    # for part in dataParts:
    #     print(part.split(",")[0])

async def getWatch():
    possibleDevice = await searchForWatch()
    return possibleDevice

async def searchAndConnectToWatch():
    clientAddress = await searchForWatch()
    if(clientAddress is None):
        print("No watch found")
        return None
    client = await connectToWatch(clientAddress.address)
    return client

async def awaitCancellation(string: str,client : BleakClient):
    await asyncio.to_thread(sys.stdout.write, f'{string} ')
    await asyncio.to_thread(sys.stdin.readline)
    await stopRecording(client, "1234")

if __name__ == "__main__":
    asyncio.run(searchAndConnectToWatch())
    