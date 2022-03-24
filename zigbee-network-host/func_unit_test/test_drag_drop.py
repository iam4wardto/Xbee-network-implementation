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

with dpg.window(label="Dear PyGui Demo", width=800, height=800, pos=(100, 100), tag="__demo_id"):
    with dpg.tree_node(label="Simple"):
        with dpg.group(horizontal=True, xoffset=200):
            with dpg.group():
                dpg.add_text("Int Sources:")

                dpg.add_button(label="Source 1: 25")
                with dpg.drag_payload(parent=dpg.last_item(), drag_data=25, payload_type="ints"):
                    dpg.add_text("25")

                dpg.add_button(label="Source 2: 33")
                with dpg.drag_payload(parent=dpg.last_item(), drag_data=33, payload_type="ints"):
                    dpg.add_text("33")

                dpg.add_button(label="Source 3: 111")
                with dpg.drag_payload(parent=dpg.last_item(), drag_data=111, payload_type="ints"):
                    dpg.add_text("111")

            with dpg.group():
                dpg.add_text("Float Sources:")
                dpg.add_button(label="Source 1: 43.7")
                with dpg.drag_payload(parent=dpg.last_item(), drag_data=43.7, payload_type="floats"):
                    dpg.add_text("43.7")

                dpg.add_button(label="Source 2: 99.8")
                with dpg.drag_payload(parent=dpg.last_item(), drag_data=99.8, payload_type="floats"):
                    dpg.add_text("99.8")

                dpg.add_button(label="Source 3: -23.4")
                with dpg.drag_payload(parent=dpg.last_item(), drag_data=-23.4, payload_type="floats"):
                    dpg.add_text("-23.4")

            with dpg.group():
                dpg.add_text("Targets:")

                dpg.add_input_int(label="Int Target", payload_type="ints", width=100, step=0,
                                  drop_callback=lambda s, a: dpg.set_value(s, a))
                dpg.add_input_float(label="Float Target", payload_type="floats", width=100, step=0,
                                    drop_callback=lambda s, a: dpg.set_value(s, a))




# main loop
dpg.show_viewport()
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()