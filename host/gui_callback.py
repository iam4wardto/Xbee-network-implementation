import json
import dearpygui.dearpygui as dpg
from dearpygui_ext import logger
from digi.xbee.devices import *
from digi.xbee.models import *
from digi.xbee.util import utils
from net_cfg import *



## callback for xbee module

def refresh_nodes_temp_table():
    '''
    to int, refresh the temperature list when receive the related response
    :return: None
    '''
    dpg.delete_item("tableFuncPanelTemps", children_only=True)
    dpg.add_table_column(label="Node ID", parent="tableFuncPanelTemps")
    dpg.add_table_column(label="temperature", parent="tableFuncPanelTemps")
    for obj in net.nodes_obj:
        with dpg.table_row(parent="tableFuncPanelTemps"):
            dpg.add_text(obj.node_xbee.get_node_id())
            dpg.add_text(obj.temperature)

# Callback for discovered devices.
def callback_device_discovered(remote):
    net.log.log_info("Device discovered: %s" % remote.get_parameter("NI").decode())
    #print("Device discovered: {}, RSSI: {}".format(remote.get_parameter("NI").decode(),
    #                                               utils.bytes_to_int(remote.get_parameter("DB"))   ))
    print("Device discovered: {}".format(remote.get_parameter("NI").decode()))


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
    data = json.loads(data)
    #print(data.get("response"))
    for obj in net.nodes_obj:
        if obj.node_xbee.get_64bit_addr() == addr_64:
            obj.temperature = str(data.get("response")[0])
    # TODO use switch to select which function response this is
    refresh_nodes_temp_table()
