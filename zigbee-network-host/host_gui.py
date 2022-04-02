import json
import time
import math
import urllib.request

import serial.tools.list_ports as stl
from PIL import Image
from digi.xbee.devices import *
from digi.xbee.filesystem import FileSystemException, update_remote_filesystem_image
from digi.xbee.models import *
from digi.xbee.util import utils
from gui_callback import *
from helper_funcs import *

try:
    # deal with dpi issue on Windows
    import ctypes

    ctypes.windll.shcore.SetProcessDpiAwareness(2)
finally:
    pass

dpg.create_context()


def add_theme_to_gui():
    with dpg.theme(tag="__demo_hyperlinkTheme"):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 0, 0, 0])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [29, 151, 236, 25])
            dpg.add_theme_color(dpg.mvThemeCol_Text, [29, 151, 236])

    with dpg.theme(tag="themeRed"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_red)

    with dpg.theme(tag="themeRed2"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_red2)

    with dpg.theme(tag="themeGreen"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_green)

    with dpg.theme(tag="themeWhite"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_white)

    with dpg.theme(tag="themeBlue"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_blue)

    with dpg.theme(tag="themeLightGreen"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_green2)

    with dpg.theme(tag="themeWinBgBlack"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [0, 0, 0], category=dpg.mvThemeCat_Core)

    with dpg.theme(tag="themeGlobal") as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 9)
    dpg.bind_theme(global_theme)


def set_gui_theme():
    dpg.bind_item_theme("winMenuAbout", "themeWinBgBlack")

def _log(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


def add_image_to_gui():
    width0, height0, channels0, data0 = dpg.load_image("./figure/floodlight.png")
    width1, height1, channels1, data1 = dpg.load_image("./figure/eth_logo.png")
    width2, height2, channels2, data2 = dpg.load_image("./figure/rsl_logo_white.png")
    width3, height3, channels3, data3 = dpg.load_image("./figure/gui_demo.jpg")
    width4, height4, channels4, data4 = dpg.load_image("./figure/light_effect.jpg")

    with dpg.texture_registry():
        texture_id_0 = dpg.add_static_texture(width0, height0, data0)
        texture_id_1 = dpg.add_static_texture(width1, height1, data1)
        texture_id_2 = dpg.add_static_texture(width2, height2, data2)
        texture_id_3 = dpg.add_static_texture(width3, height3, data3)
        texture_id_4 = dpg.add_static_texture(width4, height4, data4)
    return [texture_id_0, texture_id_1, texture_id_2, texture_id_3, texture_id_4]


def _help(message):  # to add help tooltip for the last item
    last_item = dpg.last_item()
    group = dpg.add_group(horizontal=True)
    dpg.move_item(last_item, parent=group)
    dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
    t = dpg.add_text("(?)", color=[0, 255, 0])
    with dpg.tooltip(t):
        dpg.add_text(message)


def get_temp_callback():
    node_name = dpg.get_value("comboNodes")
    if node_name == 'None' or node_name is None:  # user not selected
        net.log.log_error("Please select node first.")
        return
    """
            command list encoded in JSON
            "category": 0, 1, 2, 3 i.e. device, time, led, info
            "params": same input for this function
            """
    if node_name == "All Nodes":
        target_nodes = net.available_nodes_id
    else:
        target_nodes = [node_name]

    print(target_nodes)
    for target_node in target_nodes:
        command_params = [{"category": 3, "id": 1, "params": [0]}]  # params 0 for None
        DATA_TO_SEND = json.dumps(command_params)
        send_command_to_device(target_node, DATA_TO_SEND, 3, 1)


def latency_test_callback():
    node_name = dpg.get_value("comboNodes")
    if node_name == 'None' or node_name is None:
        net.log.log_debug("Please select a node to start latency test!")
        return
    elif node_name == "All Nodes":
        net.log.log_debug("Please select a single node for payload test!")
        return

    num_msg = 10
    logging.basicConfig(filename="log.txt", filemode='a',
                        level=logging.INFO, format="%(asctime)s %(message)s")
    logging.info("\n")
    logging.info("*** latency test start ***")
    print("*** latency test start ***")

    for i in range(num_msg):

        command_params = [{"category":3, "id":1}] #24 bytes
        DATA_TO_SEND = json.dumps(command_params)

        send_command_to_device(node_name, DATA_TO_SEND, 3, 1)
        time.sleep(2.2) # should leave enough time for one response

    logging.info("*** latency test success ***")
    print("*** latency test success ***")


def payload_test_callback():

    node_name = dpg.get_value("comboNodes")
    if node_name == 'None' or node_name is None:
        net.log.log_debug("Please select a node to start payload test!")
        return
    elif node_name == "All Nodes":
        net.log.log_debug("Please select a single node for payload test!")
        return

    num_set = params.groups_payload_test
    logging.basicConfig(filename="log.txt", filemode='a',
                        level=logging.INFO, format="%(asctime)s %(message)s")
    logging.info("\n")
    logging.info("*** payload test start ***")
    print("*** payload test start ***")

    #element = {"category": 3, "id": 1, "params": [0]} # 40 bytes in total, can use 6 groups
    element = [{"category":3, "id":1}] # 24 bytes, add 2 bytes when in json, in total we test 9 group

    for i in range(num_set):

        command_params = [{"category":3, "id":1}]

        # add payload acoording to group
        for j in range(i):
            command_params.append(element)
        DATA_TO_SEND = json.dumps(command_params)

        logging.info("group {} of payload test".format(i+1))
        print("group {} of payload test".format(i+1))
        for k in range(10):
            send_command_to_device(node_name, DATA_TO_SEND, 3, 1)
            time.sleep(2.5) # should leave enough time for one response

    logging.info("*** payload test success ***")
    print("*** payload test success ***")


def get_state_callback():
    node_name = dpg.get_value("comboNodes")
    if node_name == 'None' or node_name is None:  # user not selected
        net.log.log_error("Please select node first.")
        return

    if node_name == "All Nodes":
        target_nodes = net.available_nodes_id
    else:
        target_nodes = [node_name]

    for target_node in target_nodes:
        command_params = [{"category": 0, "id": 0, "params": [0]}]  # params 0 for None
        DATA_TO_SEND = json.dumps(command_params)
        send_command_to_device(target_node, DATA_TO_SEND, 0, 0)

def get_power_callback():
    node_name = dpg.get_value("comboNodes")
    if node_name == 'None' or node_name is None:  # user not selected
        net.log.log_error("Please select node first.")
        return

    if node_name == "All Nodes":
        target_nodes = net.available_nodes_id
    else:
        target_nodes = [node_name]

    for target_node in target_nodes:
        command_params = [{"category": 0, "id": 1, "params": [0]}]  # params 0 for None
        DATA_TO_SEND = json.dumps(command_params)
        send_command_to_device(target_node, DATA_TO_SEND, 0, 1)


def sync_clock_callback():
    node_name = dpg.get_value("comboNodes")
    if node_name == 'None' or node_name is None:  # user not selected
        net.log.log_error("Please select node first.")
        return

    if node_name == "All Nodes":
        target_nodes = net.available_nodes_id
    else:
        target_nodes = [node_name]

    for target_node in target_nodes:
        command_params = [{"category": 1, "id": 0, "params": [0]}]  # params 0 for None
        DATA_TO_SEND = json.dumps(command_params)
        send_command_to_device(target_node, DATA_TO_SEND, 1, 0)


def set_color_callback():
    target_color = dpg.get_value("colorSelector") # rgba channel
    #print(target_color)
    node_name = dpg.get_value("comboNodes")
    if node_name == 'None' or node_name == None:  # user not selected
        net.log.log_error("Please select node first.")
        return

    command_params = [{"category": 2, "id": 0, "params":
        [target_color[0]/255.0,target_color[1]/255.0,target_color[2]/255.0,target_color[3]/255.0]}]
    DATA_TO_SEND = json.dumps(command_params)
    send_command_to_device(node_name, DATA_TO_SEND, 2, 0)


def com_radio_button_callback(sender, app_data):
    serial_param.PORT = app_data.partition(':')[0]
    # e.g. input app_data: "COM7: USB Serial Port (COM7)", here take COM7 out


def log_callback(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


def menuAbout_callback():
    dpg.show_item("winMenuAbout")
    centering_windows("winMenuAbout", dpg.get_viewport_client_width(), dpg.get_viewport_client_height(),
                      20 * params.scale)


def menuGettingStarted_callback():
    dpg.show_item("winMenuGettingStarted")
    centering_windows("winMenuGettingStarted", dpg.get_viewport_client_width(), dpg.get_viewport_client_height(),
                      20 * params.scale)


def max_node_view_callback(sender, app_data, user_data):
    btn_label = dpg.get_item_label("btnMaxNodeView")
    if btn_label == "Maximize":
        dpg.set_item_label("btnMaxNodeView", "Minimize")
        dpg.set_primary_window("winMain", True)
        dpg.hide_item("winLog")
        dpg.hide_item("winFuncPanel")
    else:
        dpg.set_item_label("btnMaxNodeView", "Maximize")
        dpg.set_primary_window("winMain", False)
        dpg.show_item("winLog")
        dpg.show_item("winFuncPanel")


def exit_callback():
    print("Exit called...")
    try:
        if net.coord is not None and net.coord.is_open():
            net.coord.close()
            print("COORD closed")
        #dpg.show_item("winExitConfirm")
    except:
        pass  # not relevant here


def menu_show_metric_callback():
    last_item = dpg.show_tool(dpg.mvTool_Metrics)


def btn_update_info_cancel_callback():
    dpg.hide_item("winUpdateDialog")


def ota_update_progress_callback(info: str, progress: int):
    dpg.configure_item("txtOTAUpdateStatus", default_value=info + ": " + str(progress) + "%")


def btn_update_info_proceed_callback():
    node_to_update_id = dpg.get_value("comboNodesCopy")
    ota_file_path = dpg.get_item_user_data("btnUpdateInfoProceed")
    try:
        node_to_update = net.xbee_network.discover_device(node_to_update_id)
        update_remote_filesystem_image(node_to_update, ota_filesystem_file=ota_file_path,
                                       progress_callback=ota_update_progress_callback)
        dpg.configure_item("txtOTAUpdateStatus", default_value="Device resetting...")
        node_to_update.reset()
        dpg.configure_item("txtOTAUpdateStatus", default_value="Update successful!")
    except Exception as err:
        net.log.log_error(err)
        dpg.configure_item("txtOTAUpdateStatus", default_value=str(err)[:40])


def comboNodesCopy_callback():
    if dpg.get_value("txtSelectedImage") != "Please open file selector.":
        if dpg.does_item_exist("tipBtnUpdateInfoProceed"):
            dpg.delete_item("tipBtnUpdateInfoProceed")
        dpg.configure_item("btnUpdateInfoProceed", callback=btn_update_info_proceed_callback)


def btnUpdateInfoOpen_callback():
    dpg.configure_item("winUpdateDialog", modal=False)
    dpg.show_item("winUpdateDialog")
    dpg.show_item("fileSel")
    dpg.focus_item("fileSel")


def _ota_process(sender, app_data):
    '''
    internal use for ota update menu
    :param sender:
    :param app_data: selected file address
    :return: none
    '''
    # print("Sender: ", sender)
    # print(app_data)
    dpg.configure_item("txtSelectedImage", default_value=app_data['file_name'])
    if dpg.get_value("comboNodesCopy") != 'None':
        if dpg.does_item_exist("tipBtnUpdateInfoProceed"):
            dpg.delete_item("tipBtnUpdateInfoProceed")
        dpg.configure_item("btnUpdateInfoProceed", callback=btn_update_info_proceed_callback)
    # very flexible to pass user data
    dpg.set_item_user_data("btnUpdateInfoProceed", app_data['file_path_name'])


def menu_ota_callback():
    if not dpg.does_item_exist("fileSel"):
        with dpg.file_dialog(label="Please select update image for Zigbee module",
                             show=False, directory_selector=False, tag="fileSel",
                             callback=_ota_process, file_count=0, width=500 * params.scale,
                             height=350 * params.scale, modal=True):
            dpg.add_file_extension(".ota")
            dpg.add_file_extension(".py")
    if not dpg.does_item_exist("winUpdateDialog"):
        # guarantee these commands happen in the same frame
        with dpg.mutex():
            viewport_width = dpg.get_viewport_client_width()
            viewport_height = dpg.get_viewport_client_height()
            with dpg.window(label="Zigbee OTA Update Dialog", tag="winUpdateDialog", modal=True,
                            show=True, autosize=True) as modal_id:
                with dpg.group(horizontal=True):
                    dpg.add_loading_indicator(circle_count=4)
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            dpg.add_text("Please select node:   ")
                            dpg.add_combo(dpg.get_item_configuration("comboNodes")['items'], label="",
                                          height_mode=dpg.mvComboHeight_Regular, tag="comboNodesCopy",
                                          default_value='None', callback=comboNodesCopy_callback)

                        with dpg.group(horizontal=True):
                            dpg.add_text("Selected OTA image:")
                            dpg.add_input_text(default_value='Please open file selector.', readonly=True,
                                               tag="txtSelectedImage")
                            dpg.add_button(label="open", tag="btnUpdateInfoOpen", callback=btnUpdateInfoOpen_callback)
                            dpg.bind_item_theme("btnUpdateInfoOpen", "themeBlue")
                        with dpg.group(horizontal=True):
                            dpg.add_text("Update status:           ")
                            dpg.add_input_text(default_value='', readonly=True, tag="txtOTAUpdateStatus")
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Proceed", tag="btnUpdateInfoProceed")
                            dpg.bind_item_theme("btnUpdateInfoProceed", "themeBlue")
                            dpg.add_spacer(width=25 * params.scale)
                            dpg.add_button(label="Cancel", tag="btnUpdateInfoCancel",
                                           callback=btn_update_info_cancel_callback)
                            dpg.bind_item_theme("btnUpdateInfoCancel", "themeBlue")

        centering_windows(modal_id, viewport_width, viewport_height, 40 * params.scale)

    # re-show windows, refresh info from node list
    dpg.show_item("winUpdateDialog")
    dpg.configure_item("comboNodesCopy", items=dpg.get_item_configuration("comboNodes")['items'])
    dpg.configure_item("txtOTAUpdateStatus", default_value='')

    if dpg.get_value("comboNodesCopy") == 'None' or dpg.get_value(
            "txtSelectedImage") == "Please open file selector.":  # user didn't finish selection
        dpg.configure_item("btnUpdateInfoProceed", callback=None)
        if not dpg.does_item_exist("tipBtnUpdateInfoProceed"):
            with dpg.tooltip("btnUpdateInfoProceed", tag="tipBtnUpdateInfoProceed"):
                dpg.add_text("Please finish selection first!")
    else:
        dpg.configure_item("btnUpdateInfoProceed", callback=btn_update_info_proceed_callback)
        if dpg.does_item_exist("tipBtnUpdateInfoProceed"):
            dpg.delete_item("tipBtnUpdateInfoProceed")


def winStarted_close_callback():
    dpg.configure_item("winWelcome", modal=True)


def main():
    ## create logger for Xbee Class
    dev_logger = logging.getLogger("digi.xbee.devices")
    rx_logger = logging.getLogger("digi.xbee.reader")
    tx_logger = logging.getLogger("digi.xbee.sender")

    # Get a handler and configure a formatter for it.
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ''%(message)s')
    handler.setFormatter(formatter)
    dev_logger.addHandler(handler)

    add_theme_to_gui()
    gui_image = add_image_to_gui()

    with dpg.window(label="", tag="winUpdateIndicator", pos=params.winLoadingIndicator_pos, modal=True, show=False):
        with dpg.group(horizontal=True):
            dpg.add_loading_indicator()
            dpg.add_text("Module update in progress...")

    with dpg.window(label="Main", width=400 * params.scale, height=600 * params.scale, tag="winMain",
                    no_title_bar=True, no_close=True, no_move=True):
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

                    with dpg.child_window(height=60 * params.scale, autosize_x=True, delay_search=True):
                        for i in range(10):
                            dpg.add_text(f"Scolling Text{i}")

                    dpg.add_slider_float(label="Slider Float")
                    dpg.add_input_int(label="Input Int")
                    dpg.add_combo(("Yes", "No", "Maybe"), label="Combo")

            with dpg.menu(label="Tools"):
                dpg.add_menu_item(label="Show GUI Metrics", callback=menu_show_metric_callback)
                dpg.add_menu_item(label="Zigbee OTA Update", callback=menu_ota_callback)
                dpg.add_menu_item(label="Show Style Editor", callback=lambda: dpg.show_tool(dpg.mvTool_Style))
                dpg.add_menu_item(label="Show Item Registry", callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="Set Fullscreen", check=True, callback=lambda: dpg.toggle_viewport_fullscreen())
                dpg.add_menu_item(label="Getting Started", callback=menuGettingStarted_callback)
                dpg.add_menu_item(label="About", callback=menuAbout_callback)

        with dpg.collapsing_header(label="Nodes Graph View", default_open=True):
            dpg.add_text("Link denotes network connection.", bullet=True)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Maximize", tag="btnMaxNodeView", callback=max_node_view_callback)
                dpg.add_button(label="Refresh", tag="btnRefreshAllNet", callback=btnRefresh_callback)
                if params.test_mode:
                    dpg.add_button(label="Disconnect", tag="btnDisconnectCoord", callback=btnDisconnectCoord_callback)
                    dpg.bind_item_theme("btnDisconnectCoord", "themeBlue")
                    dpg.add_button(label="Payload test", tag="btnPayloadTest", callback=payload_test_callback)
                    dpg.bind_item_theme("btnPayloadTest", "themeBlue")
                    dpg.add_button(label="Latency test", tag="btnLatencyTest", callback=latency_test_callback)
                    dpg.bind_item_theme("btnLatencyTest", "themeBlue")
                dpg.bind_item_theme("btnMaxNodeView", "themeBlue")
                dpg.bind_item_theme("btnRefreshAllNet", "themeBlue")
                with dpg.tooltip("btnRefreshAllNet"):
                    dpg.add_text("start new discovery")
                with dpg.tooltip("btnMaxNodeView"):
                    dpg.add_text("maximize node graph view")
            with dpg.node_editor(
                    callback=lambda sender, app_data: dpg.add_node_link(app_data[0], app_data[1], parent=sender),
                    delink_callback=lambda sender, app_data: dpg.delete_item(app_data), tag="nodeEditor"):
                pass
        with dpg.collapsing_header(label="Nodes List View", default_open=True):
            with dpg.tree_node(label="Node Table", default_open=True):
                with dpg.table(header_row=True, row_background=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=False, resizable=True, sortable=True, tag="tableNodes"):

                    dpg.add_table_column(label="Node ID")
                    dpg.add_table_column(label="Addr_16")
                    dpg.add_table_column(label="Status")

                    for i in range(5):  # dummy init table
                        with dpg.table_row():
                            for j in range(3):
                                dpg.add_text(f"Row{i} Column{j}")
            with dpg.tree_node(label="Network Links", default_open=True):
                with dpg.table(header_row=True, row_background=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=False, delay_search=True, tag="tableLinks"):
                    dpg.add_table_column(label="links")
                    dpg.add_table_column(label="LQI index           ",width=100*params.scale, width_fixed=True)

    with dpg.window(label="About Semester Project", tag="winMenuAbout", autosize=True, modal=False, show=False,
                    no_background=False, no_close=False, no_collapse=True):
        with dpg.table(header_row=False, row_background=False,
                       borders_innerH=False, borders_outerH=False, borders_innerV=False,
                       borders_outerV=False, resizable=False, sortable=True) as tableAbout:
            dpg.add_table_column(width=350, width_fixed=True)
            dpg.add_table_column(width_stretch=True)
            with dpg.table_row():
                dpg.add_text("Implementing Distributed Network Communication\nfor Outdoor Sensor Network\n")
                # dpg.add_text("for Outdoor Sensor Network")
                # dpg.add_text("")
                dpg.add_image(gui_image[1], width=548, height=200)
            with dpg.table_row():
                dpg.add_text("Author: Yue Li\nTeammate: Cedric Weibel\nSupervisor: Hendrik Kolvenbach, Konrad Meyer\n ")
                # dpg.add_text("Teammate: Cedric Weibel")
                # dpg.add_text("Supervisor: Hendrik Kolvenbach, Konrad Meyer")
                dpg.add_image(gui_image[2], width=408, height=160)
        dpg.add_image(gui_image[0])

    with dpg.window(label="Logger", tag="winLog", pos=params.winLog_pos, width=params.logger_width,
                    height=params.logger_height,
                    no_close=True, no_move=True):
        net.log = logger.mvLogger(parent="winLog")
        net.log.log_info("Program started.")

    with dpg.window(label="Function Panel", tag="winFuncPanel", pos=params.winFuncPanel_pos, width=params.func_width,
                    height=params.func_height, no_close=True, no_move=True):
        dpg.add_text("Current selected node:")
        items = ("A", "B", "C",)
        combo_id = dpg.add_combo(items, label="Nodes List", height_mode=dpg.mvComboHeight_Regular, tag="comboNodes")
        dpg.add_color_edit((195, 67, 100, 255), label="color selector",tag="colorSelector",callback=None)
        _help("Select color for LED control.")
        with dpg.tab_bar(tag="tabFuncPanel", reorderable=True):
            with dpg.tab(label="Node Info", tag="tabNodeInfo"):
                with dpg.table(header_row=True, row_background=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=False, resizable=True, tag="tableNodeInfoAll"):
                    add_column_tableNodeInfoAll()

            with dpg.tab(label="Device Status", tag="tabTemp"):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="get Temp", tag="btnFuncPanelGetTemp", callback=get_temp_callback)
                    dpg.add_button(label="get Status", tag="btnFuncPanelGetStatus", callback=get_state_callback)
                    dpg.add_button(label="get Power", tag="btnFuncPanelGetPower", callback=get_power_callback)
                    dpg.add_button(label="sync Clock", tag="btnFuncPanelSyncClock", callback=sync_clock_callback)

                dpg.bind_item_theme("btnFuncPanelGetTemp", "themeBlue")
                dpg.bind_item_theme("btnFuncPanelGetStatus", "themeBlue")
                dpg.bind_item_theme("btnFuncPanelGetPower", "themeBlue")
                dpg.bind_item_theme("btnFuncPanelSyncClock", "themeBlue")

                with dpg.collapsing_header(label="Nodes Temp", default_open=True):
                    with dpg.table(header_row=True, row_background=False,
                                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                   borders_outerV=False, delay_search=True, tag="tableFuncPanelTemps"):
                        dpg.add_table_column(label="Node ID")
                        dpg.add_table_column(label="temperature")
            with dpg.tab(label="LED Control", tag="tabLEDColor"):
                with dpg.table(header_row=False, row_background=False,
                            borders_innerH=False, borders_outerH=False, borders_innerV=False,
                            borders_outerV=False, delay_search=True, tag="tableLEDColor"):
                    dpg.add_table_column(label="", width = 220*params.scale,width_fixed=True)
                    dpg.add_table_column(label="")
                    with dpg.table_row():
                        with dpg.group():
                            dpg.add_slider_float(label="Brightness",min_value=0.0,max_value=1.0,format='%.2f',tag="sliderBrightness")
                            with dpg.group(horizontal=True):
                                with dpg.group():
                                    t = dpg.add_text("Light Effect      ")

                                    dpg.add_radio_button(params.light_effect, horizontal=False,
                                                         tag="radioButtonLEDEffect",callback=None,default_value="all on  ")
                                    with dpg.tooltip(t):
                                        dpg.add_image(gui_image[4],width=120*params.scale, height=184*params.scale)
                                with dpg.group():
                                    t = dpg.add_text("Confirm Node:")
                                    dpg.bind_item_theme(dpg.last_item(), "themeRed2")
                                    dpg.add_radio_button(("Single ", "Group "),horizontal=False,
                                                         tag="radioButtonNodeType",default_value="Single")
                                    with dpg.tooltip(t):
                                        dpg.add_text("Use node selector above for single node;\nto select a group, click Node Group button")
                                    dpg.add_text("Select Command:")
                                    dpg.bind_item_theme(dpg.last_item(), "themeRed2")
                                    dpg.add_checkbox(label="set Color",tag="chbColor")
                                    dpg.add_checkbox(label="set Brightness", tag="chbBrightness")
                                    dpg.add_checkbox(label="set Effect", tag="chbEffect")

                            dpg.add_spacer(height=10*params.scale)
                            with dpg.group(horizontal=True):
                                t = dpg.add_button(label="Group Node",tag="btnGroupNode",callback=btnGroupNode_callback)
                                dpg.bind_item_theme(dpg.last_item(), "themeBlue")
                                with dpg.tooltip(t):
                                    dpg.add_text("Open a widows to select node group")
                                dpg.bind_item_theme(dpg.last_item(), "themeBlue")
                                dpg.add_button(label="Send Command",tag="btnSendCommand",callback=btnSendCommand_callback)
                                dpg.bind_item_theme(dpg.last_item(), "themeBlue")

                        with dpg.group():
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=90*params.scale)
                                dpg.add_text("LED Info Table")
                            with dpg.table(header_row=True, row_background=False,
                                           borders_innerH=False, borders_outerH=False, borders_innerV=False,
                                           borders_outerV=False, delay_search=True, tag="tableNodeLEDInfo"):
                                dpg.add_table_column(label="ID")
                                dpg.add_table_column(label="Brightness")
                                dpg.add_table_column(label="Pattern")
                                dpg.add_table_column(label="Color")


            with dpg.tab(label="Location", tag="tabLocation"):
                try:
                    map_url = generate_map_url()
                    urllib.request.urlretrieve(map_url, "./figure/map.png")
                    width, height, channels, data = dpg.load_image("./figure/map.png")
                    with dpg.texture_registry():
                        texture_map = dpg.add_static_texture(width, height, data)
                    dpg.add_image(texture_map, width=params.func_width, height=int(params.func_width / 2))
                except Exception as err:
                    print(err)
                    print("network unavailable, skip map")
                    net.log.log_debug("network unavailable, skip map")
                pass

    # put this windows at last, o.t.w. "modal" doesn't work
    with dpg.window(label="Welcome", tag="winWelcome", autosize=True, pos=params.winWelcome_pos, modal=False,
                    no_close=False):
        dpg.add_text("Please select serial port to start coordinator:")
        com_list = stl.comports()
        if not com_list:
            dpg.add_text("No ports detected, check connection!", color=params.rgb_red)
        else:
            dpg.add_radio_button(tag="selComPort",
                                 items=["{}: {}".format(port, desc) for port, desc, hwid in sorted(com_list)],
                                 horizontal=False, default_value=sorted(com_list)[0],
                                 callback=com_radio_button_callback)
            with dpg.group(label="grpWelcome", horizontal=True):
                dpg.add_button(label="Open Port", tag="btnOpenPort", callback=btnOpenPort_callback,
                               user_data=dpg.get_value("selComPort"))
                dpg.bind_item_theme("btnOpenPort", "themeBlue")
                dpg.add_text("", tag="portOpenMsg")
            serial_param.PORT = sorted(com_list)[0][0]
            # if not choose, default, use first choice

    with dpg.window(label="Group Node", tag="winGroupNode", autosize=True, pos=params.winWelcome_pos, modal=True,
                    no_close=False, show=False, user_data=[]):
        with dpg.table(header_row=False, row_background=False,
                       borders_innerH=False, borders_outerH=False, borders_innerV=False,
                       borders_outerV=False, delay_search=True, tag="tableGroupNode"):

            dpg.add_table_column(label="")
            dpg.add_table_column(label="")
            dpg.add_table_column(label="")

            nodes_list = dpg.get_item_configuration("comboNodes")['items']
            if "All Nodes" in nodes_list:
                nodes_list.remove("All Nodes")
            row_num = math.ceil(len(nodes_list)/3)
            for i in range(row_num):
                with dpg.table_row():
                    for j in range(3):
                        try:
                            nodes_list[3*i+j]
                        except:
                            pass
                        else:
                            dpg.add_checkbox(label=nodes_list[3*i+j], callback=chbGroupNode_callback
                                             , user_data=nodes_list[3*i+j])


        dpg.add_spacer(height=6*params.scale)
        dpg.add_button(label="Confirm", callback=btnGroupNodeConfirm_callback)

    with dpg.window(label="Getting Started", tag="winMenuGettingStarted", autosize=True, modal=True,
                    no_background=False, no_close=False, no_collapse=True, pos=params.winStarted_pos,
                    on_close=winStarted_close_callback):
        with dpg.group(horizontal=True):
            dpg.add_loading_indicator(circle_count=4)
            with dpg.group():
                dpg.add_text("A short guide helps you through this application.")
                with dpg.group(horizontal=True):
                    dpg.add_text("The code for this GUI can be found here:")
                    hyperlink("Host GUI", "https://github.com/iam4wardto/Xbee-network-implementation")

        dpg.add_spacer(height=10 * params.scale)

        with dpg.table(header_row=False, row_background=False,
                       borders_innerH=False, borders_outerH=False, borders_innerV=False,
                       borders_outerV=False, resizable=False, sortable=True) as tableAbout:
            dpg.add_table_column(width=200, width_fixed=True)
            dpg.add_table_column(width=400, width_fixed=True)
            dpg.add_table_column(width=200, width_fixed=True)
            with dpg.table_row():
                with dpg.group():
                    dpg.add_spacer(height=6 * params.scale)
                    with dpg.tree_node(label="Main Windows", default_open=True, tag="treeMain"):
                        dpg.add_text("- Graph View")
                        dpg.add_text("- Node List")
                        dpg.add_text("- Connection List")

                dpg.add_image(gui_image[3], width=500 * params.scale, height=333 * params.scale)

                with dpg.group(horizontal=False, tag="grpWinGettingStarted"):
                    dpg.add_spacer(height=6 * params.scale)
                    with dpg.tree_node(label="Function Panel", default_open=True):
                        dpg.add_text("- Functions under Each Tab")
                        dpg.add_text("- Broadcasting")
                        dpg.add_text("- Individual Node Control")
                    dpg.add_spacer(height=150 * params.scale)
                    with dpg.tree_node(label="Logger", default_open=True):
                        dpg.add_text("- Comprehensive Log")
        dpg.bind_item_theme("treeMain", "themeLightGreen")
        dpg.bind_item_theme("grpWinGettingStarted", "themeLightGreen")

        dpg.add_spacer(height=10 * params.scale)
        dpg.add_text("* You can find this page under: Settings -> Getting Started.")

    with dpg.window(label="", tag="winLoadingIndicator", pos=params.winLoadingIndicator_pos, modal=True, show=False,
                    no_close=True):
        dpg.add_text("Network discovery in progress...")
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=params.discovery_indicator_x_offset)
            dpg.add_loading_indicator()

    # set theme
    set_gui_theme()

    # set font
    with dpg.font_registry():
        dpg.add_font("font/OpenSans-Regular.ttf", 15 * params.scale, tag="sans")
        dpg.add_font("font/Montserrat-Regular.ttf", 15 * params.scale, tag="mont")
    dpg.bind_font("mont")

    ## GUI ready
    # dpg.set_primary_window("main",True)
    dpg.create_viewport(title='Zigbee Network Host Application', small_icon='./figure/icon.ico',
                        large_icon='./figure/icon.ico',
                        width=params.main_width, height=params.main_height, x_pos=500, y_pos=200, resizable=False)
    dpg.setup_dearpygui()
    dpg.set_exit_callback(exit_callback)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == '__main__':
    main()
