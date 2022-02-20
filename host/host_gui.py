import dearpygui.dearpygui as dpg
import serial.tools.list_ports as stl
import json
import time
import gui_callback
from digi.xbee.devices import *
from digi.xbee.models import *



dpg.create_context()

class serial_param:
    PORT=""
    BAUD_RATE = 115200

# adjust all gui params here...
class params:
    def __init__(self):
        pass
    main_width = 900
    main_height = 600

    rgb_red = [255, 0, 0]
    rgb_green = [0, 255, 0]
    rgb_white = [255, 255, 255]

    coord = None

net = params() # instantiate coord module

def btnOpenPort_callback(sender, app_data, user_data):
    try:
        dpg.set_value("portOpenMsg", "Please wait...")
        dpg.bind_item_theme("portOpenMsg", "themeWhite")
        net.coord = ZigBeeDevice(serial_param.PORT, serial_param.BAUD_RATE)
        net.coord.open()
        dpg.set_value("portOpenMsg", "Success, starting...")
        dpg.bind_item_theme("portOpenMsg", "themeGreen")
        time.sleep(2)
        dpg.hide_item("winWelcome")
    except Exception as err:
        print(err)
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
    else:
        dpg.set_item_label("btnMaxNodeView", "Maximize")
        dpg.set_primary_window("winMain", False)

def exit_callback():
    print("Exit called...")
    try:
        if net.coord is not None and net.coord.is_open():
            net.coord.close()
            print("closed")
        dpg.show_item("winExitConfirm")
    except:
        pass # not relevant here


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
                dpg.add_menu_item(label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug))
                dpg.add_menu_item(label="Show Style Editor", callback=lambda: dpg.show_tool(dpg.mvTool_Style))
                dpg.add_menu_item(label="Show Item Registry", callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))

            with dpg.menu(label="Settings"):
                dpg.add_menu_item(label="Wait For Input", check=True,
                                  callback=lambda s, a: dpg.configure_app(wait_for_input=a))
                dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda: dpg.toggle_viewport_fullscreen())

        with dpg.collapsing_header(label="Network Nodes View", default_open=True):
            dpg.add_text("Link denotes parent-child.", bullet=True)
            dpg.add_button(label="Maximize", tag="btnMaxNodeView", callback=max_node_view_callback)
            with dpg.node_editor(
                    callback=lambda sender, app_data: dpg.add_node_link(app_data[0], app_data[1], parent=sender),
                    delink_callback=lambda sender, app_data: dpg.delete_item(app_data)):
                with dpg.node(label="Node 1", pos=[10, 10]):
                    with dpg.node_attribute():
                        dpg.add_input_float(label="F1", width=150)

                    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                        dpg.add_input_float(label="F2", width=150)

                with dpg.node(label="Node 2", pos=[300, 10]):
                    with dpg.node_attribute() as na2:
                        dpg.add_input_float(label="F3", width=200)

                    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                        dpg.add_input_float(label="F4", width=200)

                with dpg.node(label="Node 3", pos=[25, 150]):
                    with dpg.node_attribute():
                        dpg.add_input_text(label="T5", width=200)
                    with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                        dpg.add_simple_plot(label="Node Plot", default_value=(0.3, 0.9, 2.5, 8.9), width=200, height=80,
                                            histogram=True)


    with dpg.window(label="Confirm  Exit", tag="winExitConfirm", pos=[220, 180], modal=True, show=False):
        dpg.add_button(label="Yes", tag="btnExitConfirmYes")
        dpg.add_button(label="Cancel", tag="btnExitConfirmNo")


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