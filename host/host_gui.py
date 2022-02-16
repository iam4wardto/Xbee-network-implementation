import dearpygui.dearpygui as dpg
import serial.tools.list_ports as stl
import json
import time
from digi.xbee.devices import *
from digi.xbee.models import *



dpg.create_context()

def change_text(sender, app_data):
    dpg.set_value("text item", f"Mouse Button ID: {app_data}")

with dpg.window(label='Welcome',autosize=True, pos=[220,200], modal=True, no_close=True):
    dpg.add_text("Please select COM port to start coordinator:")
    com_list = stl.comports()
    if not com_list:
        dpg.add_text("No ports detected, check connection!")
    else:

        dpg.add_radio_button(("radio a", "radio b", "radio c"), horizontal=False, label="choiComPort")





dpg.create_viewport(title='Zigbee Network Host Application', small_icon='icon.ico', large_icon='icon.ico', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()