import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import ctypes
from dearpygui_ext.logger import mvLogger

# Include the following code before showing the viewport/calling `dearpygui.dearpygui.show_viewport`.
ctypes.windll.shcore.SetProcessDpiAwareness(2)


dpg.create_context()

with dpg.font_registry():
    font = dpg.add_font("../font/OpenSans-Regular.ttf", 15*3, tag="sans-font")
dpg.bind_font("sans-font")
dpg.set_global_font_scale(1)



dpg.create_viewport()


demo.show_demo()

# main loop
dpg.show_viewport()
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()