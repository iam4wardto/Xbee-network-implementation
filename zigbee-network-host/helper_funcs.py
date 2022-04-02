import json
import time

import dearpygui.dearpygui as dpg
import webbrowser

from typing import Union, Sequence, List
from digi.xbee.models.mode import OperatingMode
from digi.xbee.util import utils
from gui_callback import *
from net_cfg import *
import logging

def refresh_led_info_table():
    '''
    to int, refresh the temperature list when receive the related response
    :return: None
    '''
    dpg.delete_item("tableNodeLEDInfo", children_only=True)
    dpg.add_table_column(label="ID",parent="tableNodeLEDInfo")
    dpg.add_table_column(label="Brightness",parent="tableNodeLEDInfo")
    dpg.add_table_column(label="Color", parent="tableNodeLEDInfo")
    dpg.add_table_column(label="Pattern",parent="tableNodeLEDInfo")


    for obj in net.available_nodes_obj:
        with dpg.table_row(parent="tableNodeLEDInfo"):
            dpg.add_text(obj.node_xbee.get_node_id()[-4:])
            dpg.add_text(round(obj.brightness,2))
            dpg.add_color_edit(default_value=obj.rgba, label="",no_inputs=True,no_picker=True,callback=None)
            dpg.add_text(params.light_effect[obj.light_effect])


def find_node_obj_by_addr64(addr_64):
    target = next((obj for obj in net.nodes_obj if obj.node_xbee.get_64bit_addr() == addr_64))
    return target

def get_color_selector():
    target_color = dpg.get_value("colorSelector")  # rgba channel
    target_color = [round(channel / 255.0, 2) for channel in target_color]
    return target_color

def check_and_join_msg(message, addr_64):
    '''
    used to check integrity of this received msg, if get splitted one, join msg together
    In our response format, one whole msg should include even number of both '[' and ']'
    '''
    message = str(message)
    incoming_obj = next((obj for obj in net.nodes_obj if obj.node_xbee.get_64bit_addr() == addr_64), None)
    if not incoming_obj:
        raise Exception("Internal error, incoming node not found in net.nodes_obj.")

    # this message is full if and only if the 2 conditions are met
    if message.count('[') == message.count(']') and not incoming_obj.last_msg:
        return [True, message]
    else:
        # splitted msg, we save this one
        if not incoming_obj.last_msg:
            # in this case, this is the first splitted msg, we'll wait for another
            incoming_obj.last_msg = [message]
            return [False, False]
        else:
            msg_to_check = ''.join(incoming_obj.last_msg) + message
            if check_msg(msg_to_check):
                # now we get a full response in our format
                # clear saved msg for this node
                incoming_obj.last_msg = []
                print("splitted response joined.")
                return [True, msg_to_check]
            else:
                # still not a full msg if we join them together, save and wait for next
                incoming_obj.last_msg.append(message)
                return [False, False]

def check_msg(message):
    '''
    only to check integrity of this received msg
    '''
    message = str(message)
    if message.count('[') == message.count(']'):
        return True
    else:
        return False


def check_response(response,cat,id):
    '''
    return command execute status based on the received response
    '''
    if str(response) == "ERROR":
        net.log.log_error("{} executed failed on end device.".format(params.command[cat][id]))
        return False
    elif str(response) == "SUCCESS":
        net.log.log_debug("{} executed successful.".format(params.command[cat][id]))
    return True

def hyperlink(text, address):
    b = dpg.add_button(label=text, callback=lambda:webbrowser.open(address))
    dpg.bind_item_theme(b, "__demo_hyperlinkTheme")

def generate_map_url():
    map_url = "https://maps.googleapis.com/maps/api/staticmap?"\
              "size=640x320&scale=2" \
              "&maptype=roadmap" \
              "&map_id=c0881174066edcec" \
              "&key=AIzaSyBDVTILZJRnZc0Cz8QL5OlgXMpfiRr7UKw" \
              "&markers=size:mid%7Ccolor:blue%7Clabel:1%7C47.375164,8.545840"\
              "&markers=size:mid%7Ccolor:green%7Clabel:2%7C47.378155,8.545888" \
              "&markers=size:mid%7Ccolor:red%7Clabel:3%7C47.376233,8.548458"
    return map_url


def node_pos_generate(coord_pos: List[int], index: int):
    '''
    nodes are radially distributed in a hexagonal shape
    :param coord_pos: position of coordinator node
    :param index: node's order
    :return: position of this node
    '''
    pos_diff = [[-100 * params.scale, 0], [-60 * params.scale, -80 * params.scale],
                [60 * params.scale, -80 * params.scale], [100 * params.scale, 0],
                [60 * params.scale, 80 * params.scale], [-60 * params.scale, 80 * params.scale]]
    quotient = index // 6
    mod = index % 6
    scatter_size = 2
    return [coord_pos[0] + (quotient + 1) * pos_diff[mod][0] * scatter_size,
            coord_pos[1] + (quotient + 1) * pos_diff[mod][1] * scatter_size]


def centering_windows(modal_id,viewport_width,viewport_height, height_offset):
    '''
    help centering the windows/message box
    :param modal_id: windows tag
    :param viewport_width: viewport width got at run time when windows is created
    :param viewport_height: viewport height
    :return: None
    '''
    # guarantee these commands happen in another frame
    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(modal_id,
                     [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2 - height_offset])


def put_node_into_list(node):
    '''
    used when refresh node info in the list view
    :param node: xbee node object
    :return: none
    '''
    # except for new node
    id = node.get_node_id()
    if id is None: # when newly added
        id = node.get_parameter("NI").decode()

    dpg.add_text(id)
    dpg.add_text(node.get_16bit_addr())
    tmp_txt = dpg.add_text("ONLINE")
    dpg.bind_item_theme(tmp_txt, "themeGreen")

def put_node_obj_into_list(obj):
    '''
    used when refresh node info in the list view
    :param node: xbee node object
    :return: none
    '''
    dpg.add_text(obj.node_xbee.get_node_id())
    dpg.add_text(obj.node_xbee.get_16bit_addr())

    txt_tmp = dpg.add_text("ONLINE" if obj.is_available == True else "OFFLINE")
    dpg.bind_item_theme(txt_tmp,"themeGreen" if obj.is_available == True else "themeRed")


def add_column_tableNodes():
    '''
    add colune in the "tableNodes"
    :return:
    '''
    dpg.add_table_column(default_sort=True, label="Node ID", parent="tableNodes")
    dpg.add_table_column(label="addr_16", parent="tableNodes")
    dpg.add_table_column(label="Status", parent="tableNodes")
    dpg.add_table_column(label="RSSI", parent="tableNodes")

def refresh_tableNodes():
    dpg.delete_item("tableNodes",children_only=True)
    add_column_tableNodes()
    with dpg.table_row(parent="tableNodes"):
        put_node_into_list(net.coord)
    for obj in net.nodes_obj:
        with dpg.table_row(parent="tableNodes"):
            put_node_obj_into_list(obj)
            if obj.is_available:
                dpg.add_text("{} dbm".format(-utils.bytes_to_int(obj.node_xbee.get_parameter("DB"))))


def add_column_tableNodeInfoAll():
    dpg.add_table_column(label="Zigbee Module",parent="tableNodeInfoAll")
    dpg.add_table_column(label="Attribute",parent="tableNodeInfoAll")
    dpg.add_table_column(label="Floodlight",parent="tableNodeInfoAll")
    dpg.add_table_column(label="Attribute",parent="tableNodeInfoAll")


def init_nodes_temp_table():
    '''
    to int, put n/a in the temperature list in function panel
    when init, only read from nodes discovered
    :return:
    '''
    dpg.delete_item("tableFuncPanelTemps", children_only=True)
    dpg.add_table_column(label="Node ID", parent="tableFuncPanelTemps")
    dpg.add_table_column(label="temperature", parent="tableFuncPanelTemps")
    for node in net.nodes:
        with dpg.table_row(parent="tableFuncPanelTemps"):
            dpg.add_text(node.get_node_id())
            dpg.add_text("n/a")


def send_command_to_device(node_name, DATA_TO_SEND, cat, id):
    for obj in net.nodes_obj:
        if obj.node_xbee.get_node_id() == node_name:
            send_response = net.coord.send_data_64_16(obj.node_xbee.get_64bit_addr(), obj.node_xbee.get_16bit_addr(),
                                                      DATA_TO_SEND)
            net.last_command_time = time.time() # log command sent time
            if send_response.transmit_status.description == "Success":
                net.log.log_info("[transmit {}.{} {}]".format(node_name,params.command[cat][id], "Success"))
            else:
                net.log.log_error("[transmit {}.{} {}]".format(node_name,params.command[cat][id],
                                                               send_response.transmit_status.description))
            return
    # if not found this node
    net.log.log_error("Internal error, selected node not in the net.")


def select_node_callback():
    # there's no node clicked callback... so attach this to mouse-click handler
    node_selected = dpg.get_selected_nodes("nodeEditor")
    if bool(node_selected)==True:
        dpg.set_value("tabFuncPanel", "tabNodeInfo")
        dpg.delete_item("tableNodeInfoAll", children_only=True)
        add_column_tableNodeInfoAll()

        node_obj = None
        if dpg.get_item_label(node_selected[0]) == net.coord.get_node_id():
            node_tmp = net.coord
            is_coord = True
        else:
            is_coord = False
            for obj in net.nodes_obj:
                if dpg.get_item_label(node_selected[0]) == obj.node_xbee.get_node_id():
                    node_tmp = obj.node_xbee
                    node_obj = obj
        with dpg.table_row(parent="tableNodeInfoAll",tag="rowNodeInfoAll1"):
            dpg.add_text("net role")
            dpg.add_text(node_tmp.get_role().description)
            dpg.add_text("device state")
        with dpg.table_row(parent="tableNodeInfoAll",tag="rowNodeInfoAll2"):
            dpg.add_text("protocol")
            dpg.add_text(node_tmp.get_protocol().description)
            dpg.add_text("IMU_state")
        try:
            with dpg.table_row(parent="tableNodeInfoAll",tag="rowNodeInfoAll3"):
                dpg.add_text("operating mode")
                mode_tmp = int.from_bytes(node_tmp.get_parameter("AP"),'little')
                for mode in OperatingMode:
                    if mode.code == mode_tmp:
                        mode_des = mode.description
                dpg.add_text(mode_des)

                dpg.add_text("GPS_state")
        except:
            # if error, doesn't need to execute following part
            net.log.log_debug("Timeout getting {} info.".format(dpg.get_item_label(node_selected[0])))
        else:
            with dpg.table_row(parent="tableNodeInfoAll",tag="rowNodeInfoAll4"):
                dpg.add_text("firmware version")
                dpg.add_text(''.join('{:02X}'.format(x) for x in node_tmp.get_parameter("VR")))
                dpg.add_text("BLE_state")
            with dpg.table_row(parent="tableNodeInfoAll",tag="rowNodeInfoAll5"):
                dpg.add_text("hardware version")
                dpg.add_text(''.join('{:02X}'.format(x) for x in node_tmp.get_parameter("HV")))
                dpg.add_text("battery voltage")
            with dpg.table_row(parent="tableNodeInfoAll",tag="rowNodeInfoAll6"):
                dpg.add_text("power level")
                dpg.add_text(node_tmp.get_power_level().description)
                dpg.add_text("current draw")
            with dpg.table_row(parent="tableNodeInfoAll"):
                dpg.add_text("temperature")
                # byte array to hex string, then to string, e.g. 0987 mv, then to int, then to str
                #dpg.add_text(''.join([str(int(''.join('{:02X}'.format(x) for x in node_tmp.get_parameter("TP")),16))," °C"]))
                dpg.add_text(''.join([str(int.from_bytes(node_tmp.get_parameter("TP"),'big')), " °C"]))
            with dpg.table_row(parent="tableNodeInfoAll"):
                dpg.add_text("voltage supplied")
                dpg.add_text(''.join([str(int.from_bytes(node_tmp.get_parameter("%V"),'big'))," mV"]))

            if node_obj is not None: # node is not COORD
                with dpg.table_row(parent="tableNodeInfoAll"):
                    dpg.add_text("handshake time")
                    if node_obj.handshake_time is None:
                        dpg.add_text("None")
                    else:
                        format_time = time.gmtime(node_obj.handshake_time)
                        dpg.add_text("{}:{}:{}".format(format_time.tm_hour,format_time.tm_min,format_time.tm_sec))

            if not is_coord:
                if node_obj.device_state is None or node_obj.voltage is None:
                    # we send command to get info
                    node_name = node_tmp.get_node_id()
                    # get_state and power
                    DATA_TO_SEND = json.dumps([{"category": 0, "id": 0, "params": [0]},
                                               {"category": 0, "id": 1, "params": [0]}])
                    send_command_to_device(node_name, DATA_TO_SEND, 0, 0)

            if not is_coord:
                # wait for ESP's respond for get device state and power
                if node_obj.device_state is None or node_obj.voltage is None:
                    time.sleep(1.4)

                # add floodlight's info to NodeInfoAll
                dpg.add_text(node_obj.device_state,parent="rowNodeInfoAll1")
                dpg.add_text(node_obj.IMU_state,   parent="rowNodeInfoAll2")
                dpg.add_text(node_obj.GPS_state,   parent="rowNodeInfoAll3")
                dpg.add_text(node_obj.BLE_state,   parent="rowNodeInfoAll4")
                dpg.add_text("{} V".format(node_obj.voltage) if node_obj.voltage is not None else "n/a",parent="rowNodeInfoAll5")
                dpg.add_text("{} mA".format(node_obj.current_draw) if node_obj.current_draw is not None else "n/a",parent="rowNodeInfoAll6")


    dpg.clear_selected_nodes("nodeEditor")

def draw_node(node, coord_pos, index):
    id = node.get_node_id()
    if id is None or id == 'None': # when newly added
        id = node.get_parameter("NI").decode()
    with dpg.node(label=id, pos=node_pos_generate(coord_pos, index),
                  tag=''.join(['node', id, 'Graph']), parent="nodeEditor") as node_here:
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_text("addr_64:\n{}".format(node.get_64bit_addr()))
            dpg.add_text("addr_16:{}".format(node.get_16bit_addr()))
            tmp_txt = dpg.add_text(default_value="status: {}".format("ONLINE"), tag=''.join(['txt', id, 'Status']))
            dpg.bind_item_theme(tmp_txt,"themeGreen")
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag='-'.join([id, 'input'])):
            # dpg.add_text("Network Link")
            pass
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag='-'.join([id, 'output'])):
            # dpg.add_text("Network Link")
            pass

    # denotes node online, true if we just draw it
    dpg.set_item_user_data(node_here, 1)

    # after draw a node, save the next drawing index for node_pos_generate()
    dpg.set_item_user_data("nodeEditor", index + 1)

def refresh_node_info_and_add_to_main_windows():
    dpg.delete_item("nodeEditor", children_only=True)

    with dpg.handler_registry() as mouse_handler:
        m_click_left = dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left,
                                                   callback=select_node_callback)

    with dpg.node(label="COORDINATOR", pos=params.coord_pos, parent="nodeEditor"):
        # first add coord node, then add all the routers in the net
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_text("addr_64:\n{}".format(net.coord.get_64bit_addr()))
            dpg.add_text("addr_16:{}".format(net.coord.get_16bit_addr()))
            panid = utils.hex_to_string(net.coord.get_pan_id())
            panid = panid.replace(" ", "").strip("0")  # delete space and zeros
            dpg.add_text("PAN ID:{}".format(panid))

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag='-'.join([net.coord.get_node_id(), 'output'])):
            dpg.add_text("Network Link")

    # also refresh node list here
    dpg.delete_item("tableNodes", children_only=True)
    add_column_tableNodes()
    with dpg.table_row(parent="tableNodes"):
        put_node_into_list(net.coord)

    net.nodes_obj.clear()       # clear list of our container object for each node, ready for construct
    net.available_nodes.clear() # clear list of tracked nodes

    if net.enable_nodes_cache_check:
        nodes_checked = []
        for node in net.nodes:
            try:
                node.get_parameter("NI").decode()
            except:
                print("node {} check error, ignored.".format(node.get_node_id()))
            else:
                nodes_checked.append(node)
        net.nodes = nodes_checked

    # prioritize this for loop, because drawings take time
    # we want to construct net.nodes_obj a.s.a.p
    for index, node in enumerate(net.nodes):
        # inherit <RemoteXbeeDevice> class, and construct <node_container> object *important!
        tmp_obj = node_container(node)
        net.nodes_obj.append(tmp_obj)

    # assign currently discovered nodes
    net.available_nodes = net.nodes
    net.available_nodes_obj = net.nodes_obj
    net.available_nodes_id = [node.get_node_id() for node in net.available_nodes]



    for obj in net.nodes_obj:
        # get rssi value of each node using AT command "DB"
        obj.rssi = -utils.bytes_to_int(obj.node_xbee.get_parameter("DB"))

    print("total nodes to draw: {}".format(len(net.nodes)))
    for index, node in enumerate(net.nodes, start=2):
        #print("draw node as index {}".format(index))
        id = node.get_node_id()

        # on node_editor
        draw_node(node, params.coord_pos, index)

        # 1: online; 0: offline. used for graph view update when check status
        dpg.set_item_user_data(''.join(['node', id, 'Graph']),1)
        dpg.bind_item_theme(''.join(['txt', id, 'Status']), "themeGreen")

        # put each node info into list view
        with dpg.table_row(parent="tableNodes"):
            put_node_into_list(node)
            dpg.add_text("{} dbm".format(-utils.bytes_to_int(node.get_parameter("DB"))))

    # add links found by deep discovery
    dpg.delete_item("tableLinks", children_only=True)
    dpg.add_table_column(label="links", parent="tableLinks")
    dpg.add_table_column(label="LQI index           ", parent="tableLinks",width=100*params.scale, width_fixed=True)

    try:
        '''print("*** all connections ***")
        for connect in net.connections:
            print("{} <-> {}".format(connect.node_a.get_node_id(), connect.node_b.get_node_id()))'''

        #print("**** now drawing ****")
        for connect in net.connections:
            #print("{} <-> {}".format(connect.node_a.get_node_id(), connect.node_b.get_node_id()))

            # e.g. link: ROUTER2 <->COORD; input former -> output latter, note COORD only have output when drawing
            if connect.node_a.get_role().id == 0: # implicitly check if 'COORDINATOR'
                #print("node_a is COORD")
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
                dpg.add_text("{} <-> {}".format(connect.node_a.get_node_id(), connect.node_b.get_node_id()))
                dpg.add_text("{}/{}".format(connect.lq_a2b.lq, connect.lq_b2a.lq))
    except Exception as err:
        print(err)

    # also refresh nodes in the list box "comboNodes", save id to the net object
    net.nodes_id = [node.get_node_id() for node in net.nodes]  # e.g. ['router1' 'router2']
    dpg.configure_item("comboNodes", items=net.nodes_id + ["All Nodes"])


logging.basicConfig(filename="log.txt", filemode='a',
                        level=logging.INFO, format="%(asctime)s %(message)s")
logging.info("\n")
logging.info("environment: staircase - with 0 node between - in a chain")




