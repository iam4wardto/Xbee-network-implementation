import dearpygui.dearpygui as dpg
#
import json
import time
from digi.xbee.devices import *
from digi.xbee.models import *
from digi.xbee.util import utils

dpg.create_context()

## xbee module part
# test list
# serial setting
PORT = "COM7"
BAUD_RATE = 115200
PARAM_NODE_ID = "NI"
coord = ZigBeeDevice(PORT, BAUD_RATE)

coord_pos = [20,150]
# Callback for discovery finished.
def callback_discovery_finished(status):
    pass


# Callback for discovered devices.
def callback_device_discovered(remote):
    print("Device discovered: %s" % remote.get_parameter(PARAM_NODE_ID).decode())


# Callback for discovery finished. # TODO print this to gui -ing
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
    print("nodes in network:", len(nodes) + 1)
    for node in nodes:
        print("node:", node.get_64bit_addr(), '-', node.get_node_id())
    connections = xbee_network.get_connections()
    for connect in connections:
        print("link:{}<->{}".format(connect.node_a.get_node_id(), connect.node_b.get_node_id()))
    # class digi.xbee.devices.Connection

finally:
    pass




# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)

# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    dpg.delete_item(app_data)

def main_maximize_callback(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    btn_label = dpg.get_item_label("btnMax")
    if btn_label == "Maximize":
        dpg.set_item_label("btnMax","Minimize")
        dpg.set_primary_window("winMain",True)
    else:
        dpg.set_item_label("btnMax", "Maximize")
        dpg.set_primary_window("winMain", False)

def log_callback(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")

def delete_node_callback(sender, app_data, user_data):
    dpg.delete_item("nodeEditor",children_only=True)

def node_pos_generate(coord_pos: [int,int],index: int):
    '''
    nodes are radially distributed in a hexagonal shape
    :param coord_pos: position of coordinator node
    :param index: node's order
    :return: position of this node
    '''
    pos_diff=[[-100,0],[-60,-80],[60,-80],[100,0],[60,80],[-60,80]]
    quotient = index // 6
    mod = index % 6
    scatter_size =2
    return [coord_pos[0]+(quotient+1)*pos_diff[mod][0]*scatter_size,
            coord_pos[1]+(quotient+1)*pos_diff[mod][1]*scatter_size]

with dpg.window(label="Tutorial", width=400, height=400,tag="winMain"):

    dpg.add_text("Link denotes parent-child.", bullet=True)
    with dpg.group(horizontal=True):
        # test maximize node editor view
        dpg.add_button(label="Maximize",tag="btnMax",callback=main_maximize_callback)
        # test delete item of node editor
        dpg.add_button(label="DelNode", tag="btnDeleteNode", callback=delete_node_callback)
    with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, tracked=True,tag="nodeEditor"):
        with dpg.node(label="COORDINATOR", pos=coord_pos):
            # first add coord node, then add all the routers in the net
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_text("addr_64:\n{}".format(coord.get_64bit_addr()))
                dpg.add_text("addr_16:{}".format(coord.get_16bit_addr()))
                panid = utils.hex_to_string(coord.get_pan_id())
                panid = panid.replace(" ","").strip("0") #delete space and zeros
                dpg.add_text("PAN ID:{}".format(panid))

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output,tag='-'.join(['COORD','output'])):
                dpg.add_text("Network Link")

        for index, node in enumerate(nodes,start=2):
            id = node.get_node_id()
            with dpg.node(label=id, pos=node_pos_generate(coord_pos,index)):
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                    dpg.add_text("addr_64:\n{}".format(node.get_64bit_addr()))
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input,tag='-'.join([id,'input'])):
                    #dpg.add_text("Network Link")
                    pass
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output,tag='-'.join([id,'output'])):
                    #dpg.add_text("Network Link")
                    pass

        # add links found by deep discovery
        for connect in connections:
            # e.g. link: ROUTER2 <->COORD; input former -> output latter, note COORD only have output when drawing
            if connect.node_a.get_node_id() == 'COORD':
                text_a = 'output'
                text_b = 'input'
            else:
                text_a = 'input'
                text_b = 'output'
            dpg.add_node_link('-'.join([connect.node_a.get_node_id(),text_a]),
                                       '-'.join([connect.node_b.get_node_id(),text_b]) , parent="nodeEditor")



dpg.add_viewport_menu_bar(label="viewport menu",tag="mainMenu")

with dpg.menu(label="Tools",parent="mainMenu"):
    dpg.add_menu_item(label="Show Metrics", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
    dpg.add_menu_item(label="Show Documentation", callback=lambda: dpg.show_tool(dpg.mvTool_Doc))
    dpg.add_menu_item(label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug))
    dpg.add_menu_item(label="Show Style Editor", callback=lambda: dpg.show_tool(dpg.mvTool_Style))
    dpg.add_menu_item(label="Show Item Registry", callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))

with dpg.menu(label="Settings",parent="mainMenu"):
    dpg.add_menu_item(label="Wait For Input", check=True,
                      callback=lambda s, a: dpg.configure_app(wait_for_input=a))
    dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda: dpg.toggle_viewport_fullscreen())



dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

#print(node_pos_generate([200,300],2))
if coord is not None and coord.is_open():
    print('closed');
    coord.close()