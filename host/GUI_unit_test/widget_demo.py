import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from dearpygui_ext.logger import mvLogger

dpg.create_context()
dpg.create_viewport()

demo.show_demo()

# main loop
dpg.show_viewport()
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()