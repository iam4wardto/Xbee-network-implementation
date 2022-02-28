import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from dearpygui_ext.logger import mvLogger

dpg.create_context()
with dpg.font_registry():
    font = dpg.add_font("OpenSans-Regular.ttf", 15*2, tag="sans-font")
dpg.bind_font("sans-font")
dpg.set_global_font_scale(0.5)



dpg.create_viewport()


demo.show_demo()

# main loop
dpg.show_viewport()
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()