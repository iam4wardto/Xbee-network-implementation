import json
import time
import dearpygui.dearpygui as dpg
from dearpygui_ext import logger
from digi.xbee.devices import *
from digi.xbee.models import *
from digi.xbee.util import utils
from net_cfg import *
from helper_funcs import *


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


# Callback for discovery finished.
def callback_discovery_finished(status):
    if status == NetworkDiscoveryStatus.SUCCESS:
        print("Discovery process finished successfully.")
        net.log.log_info("Discovery process finished successfully.")
    else:
        print("There was an error discovering devices: %s" % status.description)
        net.log.log_error(status.description)


def cb_network_modified(event_type, reason, node):
    print("  >>>> Network event:")
    print("         Type: %s (%d)" % (event_type.description, event_type.code))
    print("         Reason: %s (%d)" % (reason.description, reason.code))

    if not node:
      return

    print("         Node:")
    print("            %s" % node)


def check_node_handshake_time():
    for obj in net.nodes_obj:
        if obj.handshake_time is not None:
            if (time.time() - obj.handshake_time)>20:
                obj.is_available = False
                id = obj.node_xbee.get_node_id()
                dpg.configure_item(''.join(['txt',id, 'Status']),default_value="status:{}".format("OFFLINE"))
                dpg.bind_item_theme(''.join(['txt',id, 'Status']),"themeRed")

                # print this debug info only once
                if dpg.get_item_user_data(''.join(['node', id, 'Graph'])):
                    net.log.log_debug("Node {} offline.".format(id))
                    dpg.set_item_user_data(''.join(['node', id, 'Graph']),0)

def io_samples_callback(sample, remote, time):
    # print("New sample received from %s - %s" % (remote.get_64bit_addr(), sample))

    # if available_nodes is not empty, then net.nodes_obj is already constructed
    if net.available_nodes:
        tmp_list = [item for item in net.nodes_obj if item.node_xbee.get_64bit_addr() == remote.get_64bit_addr()]
        if tmp_list: # this incoming node is already discovered
            incoming_node = tmp_list[0]
            incoming_node.handshake_time = time

            id = incoming_node.node_xbee.get_node_id()
            # change status if OFFLINE before
            if incoming_node.is_available == False:
                dpg.configure_item(''.join(['txt', id, 'Status']), default_value="status:{}".format("ONLINE"))
                dpg.set_item_user_data(''.join(['node', id, 'Graph']), 1)
                dpg.bind_item_theme(''.join(['txt', id, 'Status']), "themeGreen")
                net.log.log_debug("Node {} online.".format(id))

            incoming_node.is_available = True
        check_node_handshake_time()


def btnOpenPort_callback(sender, app_data, user_data):
    try:
        dpg.set_value("portOpenMsg", "Please wait...")
        dpg.bind_item_theme("portOpenMsg", "themeWhite")
        net.coord = ZigBeeDevice(serial_param.PORT, serial_param.BAUD_RATE)
        if not net.coord.is_open(): # ready for refresh later
            net.coord.open()
        dpg.set_value("portOpenMsg", "Success, starting...")
        dpg.bind_item_theme("portOpenMsg", "themeGreen")

        # continue scanning...
        net.xbee_network = net.coord.get_network()
        # Configure the discovery options.
        net.xbee_network.set_deep_discovery_options(deep_mode=NeighborDiscoveryMode.FLOOD )#CASCADE
        net.xbee_network.set_deep_discovery_timeouts(node_timeout=8, time_bw_requests=5, time_bw_scans=5)
        net.xbee_network.clear()

        # add network callback
        net.xbee_network.add_device_discovered_callback(callback_device_discovered)
        net.xbee_network.add_discovery_process_finished_callback(callback_discovery_finished)
        net.xbee_network.add_network_modified_callback(cb_network_modified)
        net.coord.add_data_received_callback(coord_data_received_callback)
        net.coord.add_io_sample_received_callback(io_samples_callback)


        time.sleep(0.5)
        dpg.hide_item("winWelcome")

        net.xbee_network.start_discovery_process(deep=True, n_deep_scans=1)
        print("Discovering remote XBee devices...")
        net.log.log_info("Discovering remote XBee devices...")

        # configure loading windows
        while net.xbee_network.is_discovery_running():
            dpg.show_item("winLoadingIndicator")
        net.nodes = net.xbee_network.get_devices()
        net.connections = net.xbee_network.get_connections()
        dpg.hide_item("winLoadingIndicator")
        refresh_node_info_and_add_to_main_windows() # then we have net.nodes_obj
        init_nodes_temp_table()

    except Exception as err:
        print(err)
        net.log.log_error("Port open failed")
        dpg.set_value("portOpenMsg", "Failed, check again")
        dpg.bind_item_theme("portOpenMsg", "themeRed")

def btnRefresh_callback(sender, app_data, user_data):
    net.xbee_network.clear()
    net.xbee_network.start_discovery_process(deep=True, n_deep_scans=1)
    print("Discovering remote XBee devices...")
    net.log.log_info("Discovering remote XBee devices...")

    # configure loading windows
    while net.xbee_network.is_discovery_running():
        dpg.show_item("winLoadingIndicator")
    net.nodes = net.xbee_network.get_devices()
    net.connections = net.xbee_network.get_connections()
    dpg.hide_item("winLoadingIndicator")
    refresh_node_info_and_add_to_main_windows()
    init_nodes_temp_table()


# Callback for coord when receive data
def coord_data_received_callback(xbee_message):
    addr_64 = xbee_message.remote_device.get_64bit_addr()
    data = xbee_message.data.decode("utf8")
    print("Received data from %s: %s" % (addr_64, data))

    # TODO use switch to select which function response this is
    try:
        mes_time = xbee_message.timestamp # returned by time.time(): 1234892919.655932
        data = json.loads(data)
    except: # other api frames, not generated by our response
        pass
    else: # json decode success, then
        if data.get("category") == -1: # device power-on event
            pass
        elif data.get("category") == 3:
            for obj in net.nodes_obj:
                if obj.node_xbee.get_64bit_addr() == addr_64:
                    obj.temperature = str(data.get("response")[0])

            refresh_nodes_temp_table()



