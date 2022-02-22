# this application is for the Xbee3 coordinator connected to the PC
# send command from the PC and receive response
import json
import time
from digi.xbee.devices import *
from digi.xbee.models import *

# serial setting
PORT = "COM7"
BAUD_RATE = 115200


def print_nodes(xb_net):
    print("\nCurrent network nodes:\n    ", end='')
    if xb_net.has_devices():
        print("%s" % '\n    '.join(map(str, xb_net.get_devices())))
    else:
        print("None")


# Callback for discovered devices.
def callback_device_discovered(remote):
    print("Device discovered: %s" % remote.get_64bit_addr())


# Callback for discovery finished. # TODO print this to gui
def callback_discovery_finished(status):
    if status == NetworkDiscoveryStatus.SUCCESS:
        print("Discovery process finished successfully.")
    else:
        print("There was an error discovering devices: %s" % status.description)


# Callback for coord when receive data
def coord_data_received_callback(xbee_message):
    addr_64 = xbee_message.remote_device.get_64bit_addr()
    data = xbee_message.data.decode("utf8")
    print("Received data from %s: %s" % (addr_64, data))
    data = json.loads(data)
    print(data.get("response"))
    print(type(data.get("response")))


def main():
    print(" +-----------------------+")
    print(" | XBee Host Application |")
    print(" +-----------------------+\n")

    coord = ZigBeeDevice(PORT, BAUD_RATE)

    try:
        coord.open()

        xbee_network = coord.get_network()

        # Configure the discovery options.
        xbee_network.set_deep_discovery_options(deep_mode=NeighborDiscoveryMode.CASCADE,
                                        del_not_discovered_nodes_in_last_scan=False)
        xbee_network.set_deep_discovery_timeouts(node_timeout=20, time_bw_requests=10,
                                        time_bw_scans=20)

        xbee_network.clear()
        xbee_network.add_device_discovered_callback(callback_device_discovered)
        xbee_network.add_discovery_process_finished_callback(callback_discovery_finished)
        coord.add_data_received_callback(coord_data_received_callback)

        xbee_network.start_discovery_process(deep=True, n_deep_scans=1)

        print("Discovering remote XBee devices...")

        while xbee_network.is_discovery_running():
            time.sleep(0.1)

        # current nodes, exclude coord
        nodes = xbee_network.get_devices()
        print("nodes in network:", len(nodes)+1)
        for node in nodes:
            print("node:", node.get_64bit_addr(),'-',node.get_node_id())
        #print(nodes[0].get_node_id()) # cannot get node_id of remote module

        # send data test
        """
        command list encoded in JSON
        "category": 0, 1, 2, 3 i.e. device, time, led, info
        "params": same input for this function
        """
        command_params = {"category": 3, "id": 6, "params": [6, True]}
        DATA_TO_SEND = json.dumps(command_params)
        # xbee.COORDINATOR_ADDRESS
        send_response = coord.send_data_64_16(nodes[0].get_64bit_addr(), nodes[0].get_16bit_addr(), DATA_TO_SEND)
        print(send_response.transmit_status, type(send_response.transmit_status))

        # coord receive test
        print("Waiting for data...\n")
        #input()
        time.sleep(40)


    finally:
        if coord is not None and coord.is_open():
            coord.close()


if __name__ == '__main__':
    main()
