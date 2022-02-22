from digi.xbee.devices import *
from digi.xbee.models import *
from digi.xbee.util import utils
from net_cfg import *


## callback for xbee module

# Callback for discovered devices.
def callback_device_discovered(remote):
    print("Device discovered: %s" % remote.get_parameter("NI").decode())
    net.log.log_info("Device discovered: %s" % remote.get_parameter("NI").decode())


# Callback for discovery finished. # TODO print this to gui -ing
def callback_discovery_finished(status):
    if status == NetworkDiscoveryStatus.SUCCESS:
        print("Discovery process finished successfully.")
        net.log.log_info("Discovery process finished successfully.")
    else:
        print("There was an error discovering devices: %s" % status.description)

# Callback for coord when receive data
def coord_data_received_callback(xbee_message):
    addr_64 = xbee_message.remote_device.get_64bit_addr()
    data = xbee_message.data.decode("utf8")
    print("Received data from %s: %s" % (addr_64, data))