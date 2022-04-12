# running on xbee3 module connected to the esp32
# responsible for transfer and receive in API frame

import sys
import xbee
import time
import json
from machine import Pin
from sys import stdin, stdout


def find_device(node_id):
    """
    Finds the XBee device with the given node id
    :param node_id: Node identifier of the XBee device to find.
    :return: XBee device with the given node id or ``None``
    """
    for dev in xbee.discover():
        if dev['node_id'] == node_id:
            return dev
    return None


def send_power_on_message():
    DATA_TO_SEND = json.dumps({"category": -1, "id": 0, "response": None})
    xbee.transmit(xbee.ADDR_COORDINATOR, DATA_TO_SEND)


def status_cb(status):
    if status == 0x02:
        print("0x02 Joined network")
        send_power_on_message()
    '''if status == 0x00: # not receiving this status
        for i in range(100):
            print("received 0x00")
            time.sleep_ms(200)'''

    print("Received status: {:02X}".format(status))


def init_xbee():
    addr_64_low = ''.join('{:02X}'.format(x) for x in xbee.atcmd('SL'))
    NODE_ID = '-'.join(['ROUTER', addr_64_low[-4:]])

    xbee_settings = {"NI": NODE_ID, "CE": 0, "ID": 0x1219,"PS": 1, 'NW': 1, 'IR':0x1F40}
    # NI: readable node id, change separately
    # CE: start network, 1 for coord
    # ID: 64bit-PAN-id of our network
    # PS: micropython code auto start
    for command, value in xbee_settings.items():
        xbee.atcmd(command, value)
    xbee.atcmd("AC")  # Apply changes
    time.sleep(1)
    # enable a PIN for I/O sampling
    Pin.board.D1.mode(Pin.IN)
    '''print("Connecting to network, please wait...")
    while xbee.atcmd("AI") != 0:
        time.sleep(1)
    print("Connected to Network")'''


def main():
    #xbee.modem_status.callback(status_cb)
    init_xbee()
    try:
        send_power_on_message() # always send handshake when power on
    except:
        #print("COORD not available")
        pass

    #TARGET_ADDR = ''.join('{:02X}'.format(x) for x in xbee.ADDR_COORDINATOR)
    TARGET_NODE_ID = "COORDINATOR"

    #print("Receiving and transmitting...")
    while True:
        message = xbee.receive()
        if message:
            print(message['payload'].decode('utf-8','ignore')) # bytes object
        else:
            pass

        response = stdin.buffer.read()
        if response:
            xbee.transmit(xbee.ADDR_COORDINATOR, response)

if __name__ == '__main__':
    main()
