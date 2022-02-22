import dearpygui.dearpygui as dpg
from dearpygui_ext import logger
import serial.tools.list_ports as stl
import json
import time
from gui_callback import *
from digi.xbee.devices import *
from digi.xbee.models import *
from digi.xbee.util import utils
from net_cfg import *


dpg.create_context()

'''with dpg.font_registry():
    # Download font here: https://fonts.google.com/specimen/Open+Sans
    font = dpg.add_font("font/OpenSans-Regular.ttf", 15*2, tag="sans-font")
dpg.bind_font("sans-font")
dpg.set_global_font_scale(0.5)'''

class serial_param:
    PORT=""
    BAUD_RATE = 115200

# adjust all gui params here...
class params:
    def __init__(self):
        pass
    # position
    main_width = 900
    main_height = 600
    logger_width = 500
    logger_height = 250
    coord_pos = [20, 200] # coord pos in the node editor

    # color
    rgb_red = [255, 0, 0]
    rgb_green = [0, 255, 0]
    rgb_white = [255, 255, 255]


#net = params() # instantiate coord module


def btnOpenPort_callback(sender, app_data, user_data):
    try:
        dpg.set_value("portOpenMsg", "Please wait...")
        dpg.bind_item_theme("portOpenMsg", "themeWhite")
        net.coord = ZigBeeDevice(serial_param.PORT, serial_param.BAUD_RATE)
        net.coord.open()
        dpg.set_value("portOpenMsg", "Success, starting...")
        dpg.bind_item_theme("portOpenMsg", "themeGreen")
        time.sleep(1)
        dpg.hide_item("winWelcome")

        # continue scanning...
        net.xbee_network = net.coord.get_network()
        # Configure the discovery options.
        net.xbee_network.set_deep_discovery_options(deep_mode=NeighborDiscoveryMode.CASCADE,)
        net.xbee_network.set_deep_discovery_timeouts(node_timeout=15, time_bw_requests=5,time_bw_scans=5)
        net.xbee_network.clear()
        net.xbee_network.add_device_discovered_callback(callback_device_discovered)
        net.xbee_network.add_discovery_process_finished_callback(callback_discovery_finished)
        net.coord.add_data_received_callback(coord_data_received_callback)

        net.xbee_network.start_discovery_process(deep=True, n_deep_scans=1)
        print("Discovering remote XBee devices...")
        net.log.log_info("Discovering remote XBee devices...")

        # configure loading windows
        while net.xbee_network.is_discovery_running():
            dpg.show_item("winLoadingIndicator")
        net.nodes = net.xbee_network.get_devices()
        net.connections = net.xbee_network.get_connections()
        dpg.hide_item("winLoadingIndicator")
        refresh_node_editor()

    except Exception as err:
        print(err)
        net.log.log_error("Port open failed")
        dpg.set_value("portOpenMsg", "Failed, check again")
        dpg.bind_item_theme("portOpenMsg", "themeRed")

def com_radio_button_callback(sender, app_data):
    serial_param.PORT = app_data.partition(':')[0]
    # e.g. input app_data: "COM7: USB Serial Port (COM7)", here take COM7 out

def log_callback(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")

def max_node_view_callback(sender, app_data, user_data):
    btn_label = dpg.get_item_label("btnMaxNodeView")
    if btn_label == "Maximize":
        dpg.set_item_label("btnMaxNodeView","Minimize")
        dpg.set_primary_window("winMain",True)
        dpg.hide_item("winLog")
    else:
        dpg.set_item_label("btnMaxNodeView", "Maximize")
        dpg.set_primary_window("winMain", False)
        dpg.show_item("winLog")

def exit_callback():
    print("Exit called...")
    try:
        if net.coord is not None and net.coord.is_open():
            net.coord.close()
            print("closed")
        dpg.show_item("winExitConfirm")
    except:
        pass # not relevant here

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

def put_node_into_list(node):
    '''
    used when refresh node info in the list view
    :param node: xbee node object
    :return: none
    '''
    dpg.add_text(node.get_node_id())
    dpg.add_text(node.get_64bit_addr())
    dpg.add_text(node.get_16bit_addr())

def refresh_node_editor():
    dpg.delete_item("nodeEditor",children_only=True)
    with dpg.node(label="COORDINATOR", pos=params.coord_pos,parent="nodeEditor"):
        # first add coord node, then add all the routers in the net
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_text("addr_64:\n{}".format(net.coord.get_64bit_addr()))
            dpg.add_text("addr_16:{}".format(net.coord.get_16bit_addr()))
            panid = utils.hex_to_string(net.coord.get_pan_id())
            panid = panid.replace(" ", "").strip("0")  # delete space and zeros
            dpg.add_text("PAN ID:{}".format(panid))

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag='-'.join(['COORD', 'output'])):
            dpg.add_text("Network Link")

    # also refresh node list here
    dpg.delete_item("tableNodes", children_only=True)
    dpg.add_table_column(label="Node ID", parent="tableNodes")
    dpg.add_table_column(label="addr_64", parent="tableNodes")
    dpg.add_table_column(label="addr_16", parent="tableNodes")
    with dpg.table_row(parent="tableNodes"):
        put_node_into_list(net.coord)

    for index, node in enumerate(net.nodes, start=2):
        id = node.get_node_id()
        with dpg.node(label=id, pos=node_pos_generate(params.coord_pos, index),parent="nodeEditor"):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_text("addr_64:\n{}".format(node.get_64bit_addr()))
                dpg.add_text("addr_16:{}".format(node.get_16bit_addr()))
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag='-'.join([id, 'input'])):
                # dpg.add_text("Network Link")
                pass
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag='-'.join([id, 'output'])):
                # dpg.add_text("Network Link")
                pass
        with dpg.table_row(parent="tableNodes"):
            put_node_into_list(node)

    # add links found by deep discovery
    dpg.delete_item("tableLinks", children_only=True)
    dpg.add_table_column(label="test", parent="tableLinks")
    for connect in net.connections:
        # e.g. link: ROUTER2 <->COORD; input former -> output latter, note COORD only have output when drawing
        if connect.node_a.get_node_id() == 'COORD':
            text_a = 'output'
            text_b = 'input'
        else:
            text_a = 'input'
            text_b = 'output'
        # draw links in the graph view
        dpg.add_node_link('-'.join([connect.node_a.get_node_id(), text_a]),
                          '-'.join([connect.node_b.get_node_id(), text_b]), parent="nodeEditor")
        # add/refresh links to the list view
        with dpg.table_row(parent="tableLinks"):
            dpg.add_text("link:{}<->{}".format(connect.node_a.get_node_id(), connect.node_b.get_node_id()))



def main():
    ## add item THEME here
    with dpg.theme(tag="themeRed"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_red)

    with dpg.theme(tag="themeGreen"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_green)

    with dpg.theme(tag="themeWhite"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_white)


    with dpg.window(label="Main", width=400, height=600, tag="winMain",
                    no_title_bar=True,no_close=True, no_move=True):
        # main windows pos in default upper-left corner
        with dpg.menu_bar():
            with dpg.menu(label="Menu"):
                dpg.add_text("This menu is just for show!")
                dpg.add_menu_item(label="New")
                dpg.add_menu_item(label="Open")

                with dpg.menu(label="Open Recent"):
                    dpg.add_menu_item(label="harrel.c")
                    dpg.add_menu_item(label="patty.h")
                    dpg.add_menu_item(label="nick.py")

                dpg.add_menu_item(label="Save")
                dpg.add_menu_item(label="Save As...")

                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(label="Option 1", callback=log_callback)
                    dpg.add_menu_item(label="Option 2", check=True, callback=log_callback)
                    dpg.add_menu_item(label="Option 3", check=True, default_value=True, callback=log_callback)

                    with dpg.child_window(height=60, autosize_x=True, delay_search=True):
                        for i in range(10):
                            dpg.add_text(f"Scolling Text{i}")

                    dpg.add_slider_float(label="Slider Float")
                    dpg.add_input_int(label="Input Int")
                    dpg.add_combo(("Yes", "No", "Maybe"), label="Combo")

            with dpg.menu(label="Tools"):
                dpg.add_menu_item(label="Show Metrics", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
                dpg.add_menu_item(label="Show Documentation", callback=lambda: dpg.show_tool(dpg.mvTool_Doc))
                dpg.add_menu_item(label="Show Style Editor", callback=lambda: dpg.show_tool(dpg.mvTool_Style))
                dpg.add_menu_item(label="Show Item Registry", callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="Wait For Input", check=True,
                                  callback=lambda s, a: dpg.configure_app(wait_for_input=a))
                dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda: dpg.toggle_viewport_fullscreen())

        with dpg.collapsing_header(label="Nodes Graph View", default_open=True):
            dpg.add_text("Link denotes network connection.", bullet=True)
            dpg.add_button(label="Maximize", tag="btnMaxNodeView", callback=max_node_view_callback)
            with dpg.node_editor(
                    callback=lambda sender, app_data: dpg.add_node_link(app_data[0], app_data[1], parent=sender),
                    delink_callback=lambda sender, app_data: dpg.delete_item(app_data),tag="nodeEditor"):
                pass
        with dpg.collapsing_header(label="Nodes List View", default_open=True):
            with dpg.tree_node(label="Node Table",default_open=True):
                with dpg.table(header_row=True, row_background=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=False, delay_search=True,tag="tableNodes") as table_id:

                    dpg.add_table_column(label="Node ID")
                    dpg.add_table_column(label="addr_64")
                    dpg.add_table_column(label="addr_16")

                    for i in range(5): # dummy init table
                        with dpg.table_row():
                            for j in range(3):
                                dpg.add_text(f"Row{i} Column{j}")
            with dpg.tree_node(label="Network Links", default_open=False):
                with dpg.table(header_row=False, row_background=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=False, delay_search=True, tag="tableLinks") :
                    pass



    with dpg.window(label="Confirm  Exit", tag="winExitConfirm", pos=[220, 180], modal=True, show=False):
        dpg.add_button(label="Yes", tag="btnExitConfirmYes")
        dpg.add_button(label="Cancel", tag="btnExitConfirmNo")

    with dpg.window(label="logger",tag="winLog", pos=[400, 350],width=params.logger_width,height=params.logger_height,
                    no_close=True,no_move=True):
        net.log = logger.mvLogger(parent="winLog")

    # put this windows at last, o.t.w。 "modal" doesn't work
    with dpg.window(label="Welcome",tag="winWelcome",autosize=True, pos=[220,180], modal=True, no_close=True):
        dpg.add_text("Please select COM port to start coordinator:")
        com_list = stl.comports()
        com_list_2 = [] # test
        if not com_list:
            dpg.add_text("No ports detected, check connection!", color=params.rgb_red)
        else:
            dpg.add_radio_button(tag="selComPort", items=["{}: {}".format(port, desc) for port, desc, hwid in sorted(com_list)],
                                 horizontal=False, default_value= sorted(com_list)[0],callback=com_radio_button_callback)
            with dpg.group(label= "grpWelcome", horizontal=True):
                dpg.add_button(label="Open Port", tag="btnOpenPort", callback= btnOpenPort_callback, user_data=dpg.get_value("selComPort"))
                dpg.add_text("", tag="portOpenMsg")
            serial_param.PORT = sorted(com_list)[0][0]
            # if not choose, default, use first choice

    with dpg.window(label="",tag="winLoadingIndicator", pos=[400, 200], modal=True, show=False,no_close=True):
        dpg.add_text("Network discovery in progress...")
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=80)
            dpg.add_loading_indicator()


    ## GUI ready
    #dpg.set_primary_window("main",True)
    dpg.create_viewport(title='Zigbee Network Host Application', small_icon='icon.ico', large_icon='icon.ico',
                        width=params.main_width, height=params.main_height, x_pos=500,y_pos=200,resizable=False)
    dpg.setup_dearpygui()
    dpg.set_exit_callback(exit_callback)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()