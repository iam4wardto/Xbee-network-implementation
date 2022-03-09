import serial.tools.list_ports as stl
import json
import time

from digi.xbee.devices import *
from digi.xbee.models import *
from digi.xbee.util import utils
from digi.xbee.filesystem import FileSystemException,update_remote_filesystem_image

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
    with dpg.theme(tag="themeRed"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_red)

    with dpg.theme(tag="themeGreen"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_green)

    with dpg.theme(tag="themeWhite"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_white)

    with dpg.theme(tag="themeBlue"):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, params.rgb_blue)

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5,9)
    dpg.bind_theme(global_theme)


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
    if node_name == None:  # user not selected
        return
    """
            command list encoded in JSON
            "category": 0, 1, 2, 3 i.e. device, time, led, info
            "params": same input for this function
            """
    command_params = {"category": 3, "id": 6, "params": [6, True]}
    DATA_TO_SEND = json.dumps(command_params)
    for obj in net.nodes_obj:
        if obj.node_xbee.get_node_id() == node_name:
            send_response = net.coord.send_data_64_16(obj.node_xbee.get_64bit_addr(), obj.node_xbee.get_16bit_addr(),
                                                      DATA_TO_SEND)
            net.log.log_debug("[{}.get_temp {}]".format(node_name, send_response.transmit_status))
            break


def com_radio_button_callback(sender, app_data):
    serial_param.PORT = app_data.partition(':')[0]
    # e.g. input app_data: "COM7: USB Serial Port (COM7)", here take COM7 out


def log_callback(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


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
        dpg.show_item("winExitConfirm")
    except:
        pass  # not relevant here


def menu_show_metric_callback():
    last_item = dpg.show_tool(dpg.mvTool_Metrics)


def btn_update_info_cancel_callback():
    dpg.hide_item("winUpdateDialog")


def ota_update_progress_callback(info: str,progress: int):
    dpg.configure_item("txtOTAUpdateStatus", default_value=info+": "+str(progress)+"%")


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
    #print("Sender: ", sender)
    #print(app_data)
    dpg.configure_item("txtSelectedImage",default_value=app_data['file_name'])
    if dpg.get_value("comboNodesCopy") != 'None':
        if dpg.does_item_exist("tipBtnUpdateInfoProceed"):
            dpg.delete_item("tipBtnUpdateInfoProceed")
        dpg.configure_item("btnUpdateInfoProceed", callback=btn_update_info_proceed_callback)
    # very flexible to pass user data
    dpg.set_item_user_data("btnUpdateInfoProceed",app_data['file_path_name'])


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
                                          height_mode=dpg.mvComboHeight_Regular,tag="comboNodesCopy",
                                          default_value='None',callback=comboNodesCopy_callback)

                        with dpg.group(horizontal=True):
                            dpg.add_text("Selected OTA image:")
                            dpg.add_input_text(default_value='Please open file selector.',readonly=True,tag="txtSelectedImage")
                            dpg.add_button(label="open", tag="btnUpdateInfoOpen",callback=btnUpdateInfoOpen_callback)
                            dpg.bind_item_theme("btnUpdateInfoOpen", "themeBlue")
                        with dpg.group(horizontal=True):
                            dpg.add_text("Update status:           ")
                            dpg.add_input_text(default_value='', readonly=True, tag="txtOTAUpdateStatus")
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Proceed",tag="btnUpdateInfoProceed")
                            dpg.bind_item_theme("btnUpdateInfoProceed", "themeBlue")
                            dpg.add_spacer(width=25*params.scale)
                            dpg.add_button(label="Cancel",tag="btnUpdateInfoCancel",callback=btn_update_info_cancel_callback)
                            dpg.bind_item_theme("btnUpdateInfoCancel", "themeBlue")

        centering_windows(modal_id, viewport_width, viewport_height,40*params.scale)

    # re-show windows, refresh info
    dpg.show_item("winUpdateDialog")
    dpg.configure_item("comboNodesCopy", items=dpg.get_item_configuration("comboNodes")['items'])
    dpg.configure_item("txtOTAUpdateStatus", default_value='')

    if dpg.get_value("comboNodesCopy") == 'None' or dpg.get_value("txtSelectedImage") == "Please open file selector.": # user didn't finish selection
        dpg.configure_item("btnUpdateInfoProceed",callback=None)
        if not dpg.does_item_exist("tipBtnUpdateInfoProceed"):
            with dpg.tooltip("btnUpdateInfoProceed",tag="tipBtnUpdateInfoProceed"):
                dpg.add_text("Please finish selection first!")
    else:
        dpg.configure_item("btnUpdateInfoProceed", callback=btn_update_info_proceed_callback)
        if dpg.does_item_exist("tipBtnUpdateInfoProceed"):
            dpg.delete_item("tipBtnUpdateInfoProceed")


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
                dpg.add_menu_item(label="Wait For Input", check=True,
                                  callback=lambda s, a: dpg.configure_app(wait_for_input=a))
                dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda: dpg.toggle_viewport_fullscreen())

        with dpg.collapsing_header(label="Nodes Graph View", default_open=True):
            dpg.add_text("Link denotes network connection.", bullet=True)
            dpg.add_button(label="Maximize", tag="btnMaxNodeView", callback=max_node_view_callback)
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
                    dpg.add_table_column(label="addr_64")
                    dpg.add_table_column(label="addr_16")

                    for i in range(5):  # dummy init table
                        with dpg.table_row():
                            for j in range(3):
                                dpg.add_text(f"Row{i} Column{j}")
            with dpg.tree_node(label="Network Links", default_open=True):
                with dpg.table(header_row=True, row_background=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=False, delay_search=True, tag="tableLinks"):
                    pass

    with dpg.window(label="Confirm  Exit", tag="winExitConfirm", pos=params.winExitConfirm_pos, modal=True, show=False):
        dpg.add_button(label="Yes", tag="btnExitConfirmYes")
        dpg.add_button(label="Cancel", tag="btnExitConfirmNo")

    with dpg.window(label="Logger", tag="winLog", pos=params.winLog_pos, width=params.logger_width,
                    height=params.logger_height,
                    no_close=True, no_move=True):
        net.log = logger.mvLogger(parent="winLog")
        net.log.log_info("Program started.")

    with dpg.window(label="Function Panel", tag="winFuncPanel", pos=params.winFuncPanel_pos, width=params.func_width,
                    height=params.func_height, no_close=True, no_move=True):
        dpg.add_text("Please choose nodes...")
        items = ("A", "B", "C",)
        combo_id = dpg.add_combo(items, label="Nodes List", height_mode=dpg.mvComboHeight_Regular, tag="comboNodes")
        dpg.add_color_edit((120, 100, 200, 255), label="color selector")
        _help("Select color for LED control.")
        with dpg.tab_bar(tag="tabFuncPanel"):
            with dpg.tab(label="Node Info",tag="tabNodeInfo"):
                with dpg.table(header_row=True, row_background=False,
                               borders_innerH=True, borders_outerH=True, borders_innerV=True,
                               borders_outerV=False, resizable=True, tag="tableNodeInfoAll"):
                    add_column_tableNodeInfoAll()

            with dpg.tab(label="Temperature"):
                dpg.add_button(label="get temp", tag="btnFuncPanelGetTemp", callback=get_temp_callback)
                with dpg.collapsing_header(label="Nodes Temp", default_open=True):
                    with dpg.table(header_row=True, row_background=False,
                                   borders_innerH=True, borders_outerH=True, borders_innerV=True,
                                   borders_outerV=False, delay_search=True, tag="tableFuncPanelTemps"):
                        dpg.add_table_column(label="Node ID")
                        dpg.add_table_column(label="temperature")
            with dpg.tab(label="LED Color"):
                pass
            with dpg.tab(label="Cyclic"):
                pass

    # put this windows at last, o.t.w. "modal" doesn't work
    with dpg.window(label="Welcome", tag="winWelcome", autosize=True, pos=params.winWelcome_pos, modal=True,
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

    with dpg.window(label="", tag="winLoadingIndicator", pos=params.winLoadingIndicator_pos, modal=True, show=False,
                    no_close=True):
        dpg.add_text("Network discovery in progress...")
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=params.discovery_indicator_x_offset)
            dpg.add_loading_indicator()

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
