# running on xbee3 module connected to the esp32
# responsible for transfer and receive in API frame

import sys
import xbee
import time
from sys import stdin, stdout

def init_xbee():
    xbee_settings = {"NI": "ROUTER2", "CE": 0, "ID": 0x1219, "PS": 1}
    # NI: readable node id, change separately
    # CE: start network, 1 for coord
    # ID: 64bit-PAN-id of our network
    # PS: micropython code auto start
    for command, value in xbee_settings.items():
        xbee.atcmd(command, value)
    xbee.atcmd("AC")  # Apply changes
    time.sleep(1)
    print("Connecting to network, please wait...")
    while xbee.atcmd("AI") != 0:
        time.sleep(1)
    print("Connected to Network")


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


def main():
    init_xbee()

    TARGET_NODE_ID = "COORD"
    MESSAGE = "Hello from ROUTER1!"

    # Find the device with the configure node identifier.
    device = find_device(TARGET_NODE_ID)
    if not device:
        print("Could not find the device with node id '%s'" % TARGET_NODE_ID)
        sys.exit(-1)
    else:
        addr_16 = device['sender_nwk']
        addr_64 = device['sender_eui64']

    print("Sending data to %s >> %s" % (TARGET_NODE_ID, MESSAGE))

    try:
        # Some protocols do not have 16-bit address. In those cases, use the 64-bit one.
        xbee.transmit(addr_16 if addr_16 else addr_64, MESSAGE)
        print("Data sent successfully")
    except Exception as err:
        print("Transmit failure: %s" % str(err))

    print("Receiving and transmitting...")
    while True:
        message = xbee.receive()
        if message:
            print(message['payload'].decode('utf-8')) # bytes object
        else:
            pass
        response = stdin.buffer.read()
        if response:
            #print("response:", response)
            xbee.transmit(xbee.ADDR_COORDINATOR, response)

if __name__ == '__main__':
    main()