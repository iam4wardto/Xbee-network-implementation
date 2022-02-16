# this application is for the Xbee3 coordinator connected to the PC
# send command from the PC
# receive response and print it through serial

import xbee
import time

print("#Booting Up...")

# network state, coordinator should start the network, i.e. AI =0
while xbee.atcmd("AI") != 0:
    print("#Trying to Connect...")
    time.sleep(0.5)

print("#Online: Waiting for XBee messages...")

while True:
    received_msg = xbee.receive()
    if received_msg:
        # Get the sender's 64-bit address and payload from the received message.
        sender = received_msg['sender_eui64']
        payload = received_msg['payload']
        print("MsgFrom:%s:%s" % (''.join('{:02x}'.format(x).upper() for x in sender), payload.decode()))
