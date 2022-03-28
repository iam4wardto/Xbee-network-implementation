import json
import time
import dearpygui.dearpygui as dpg
from dearpygui_ext import logger
from digi.xbee.devices import *
from digi.xbee.models import *
from net_cfg import *
from helper_funcs import *

def radioButtonLED1_callback():
    dpg.set_value("radioButtonLED2", None)

def radioButtonLED2_callback():
    dpg.set_value("radioButtonLED1", None)

def btnGroupNode_callback():
    dpg.show_item("winGroupNode")

def btnGroupNodeConfirm_callback():
    dpg.hide_item("winGroupNode")

def chbGroupNode_callback(sender, app_data, user_data):
    selected_node = dpg.get_item_user_data("winGroupNode")
    if app_data:
        if user_data not in selected_node:
            selected_node.append(user_data)
    else:
        if user_data in selected_node:
            selected_node.remove(user_data)
    dpg.set_item_user_data("winGroupNode",selected_node)
    print(selected_node)


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
    try:
        net.log.log_info("Device discovered: %s" % remote.get_parameter("NI").decode())
        #print("Device discovered: {}, RSSI: {}".format(remote.get_parameter("NI").decode(),
        #                                               utils.bytes_to_int(remote.get_parameter("DB"))   ))
        print("Device discovered: {}".format(remote.get_parameter("NI").decode()))
    except: # leave timeout caused by cached node
        pass


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


def refresh_available_nodes():
    # refresh available nodes when status changed
    net.available_nodes = [obj.node_xbee for obj in net.nodes_obj if obj.is_available == True]
    net.available_nodes_id = [node.get_node_id() for node in net.available_nodes]
    if dpg.get_value("comboNodes") not in net.available_nodes_id:
        dpg.set_value("comboNodes", None)
    dpg.configure_item("comboNodes", items=net.available_nodes_id + ["All Nodes"])


def check_node_handshake_time():
    bool_has_editted = False
    for obj in net.nodes_obj:
        if obj.handshake_time is not None:
            if (time.time() - obj.handshake_time)>20:
                # change this node to OFFLINE, and update GUI info
                obj.is_available = False
                id = obj.node_xbee.get_node_id()
                dpg.configure_item(''.join(['txt',id, 'Status']),default_value="status: {}".format("OFFLINE"))
                dpg.bind_item_theme(''.join(['txt',id, 'Status']),"themeRed")

                # print this debug info only once
                # use user data set for each node graph, True if online
                if dpg.get_item_user_data(''.join(['node', id, 'Graph'])):
                    net.log.log_debug("Node {} offline.".format(id))
                    dpg.set_item_user_data(''.join(['node', id, 'Graph']),0)
                    bool_has_editted = True

    # change status to OFFLINE if ONLINE before
    if bool_has_editted:
        refresh_available_nodes()
        refresh_tableNodes()


def io_samples_callback(sample, remote, time):
    # print("New sample received from %s - %s" % (remote.get_64bit_addr(), sample))

    # if available_nodes is not empty, then net.nodes_obj is already constructed
    if net.available_nodes:
        tmp_list = [item for item in net.nodes_obj if item.node_xbee.get_64bit_addr() == remote.get_64bit_addr()]
        if tmp_list: # this incoming node is already discovered
            incoming_node = tmp_list[0]
            incoming_node.handshake_time = time

            id = incoming_node.node_xbee.get_node_id()

            # change status to ONLINE if OFFLINE before
            if incoming_node.is_available == False:
                dpg.configure_item(''.join(['txt', id, 'Status']), default_value="status: {}".format("ONLINE"))
                dpg.set_item_user_data(''.join(['node', id, 'Graph']), 1)
                dpg.bind_item_theme(''.join(['txt', id, 'Status']), "themeGreen")
                net.log.log_debug("Node {} online.".format(id))
                incoming_node.is_available = True
                refresh_tableNodes()

            refresh_available_nodes()
            check_node_handshake_time()

        else:
            # this is a new node, not discovered in the previous network discovery
            tmp_obj = node_container(remote)
            net.nodes_obj.append(tmp_obj)

            # add node graph
            refresh_available_nodes()
            with dpg.table_row(parent="tableNodes"):
                put_node_into_list(remote)
                dpg.add_text("{} dbm".format(-utils.bytes_to_int(remote.get_parameter("DB"))))
            draw_node(remote, params.coord_pos, dpg.get_item_user_data("nodeEditor"))
            net.log.log_info("New node {} added!".format(remote.get_node_id()))


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
        net.xbee_network.set_deep_discovery_options(deep_mode=NeighborDiscoveryMode.FLOOD,
                                                    del_not_discovered_nodes_in_last_scan = True)#CASCADE
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
    node_name = None
    try:
        node_name = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data.decode("utf8")
        print("Received data from %s: %s" % (addr_64, data))
    except:
        print("received not in response format.")

    try:
        mes_time = xbee_message.timestamp # returned by time.time(): 1234892919.655932
        data = json.loads(data)
    except: # other api frames, not in our response format, ignore here
        pass
    else: # json decode success, then
        if data.get("category") == -1: # device power-on event
            net.log.log_info("[Device {} power on.]".format(node_name))
        elif data.get("category") == 0:
            if data.get("id") == 0:  # returned state
                print(str(data.get("response")[0]))
        elif data.get("category") == 3:
            if data.get("id") == 1: # returned temperature
                for obj in net.nodes_obj:
                    if obj.node_xbee.get_64bit_addr() == addr_64: # for this node

                        if check_response(data.get("response")[0],3,1):
                            obj.temperature = str(data.get("response")[0])
                refresh_nodes_temp_table()



