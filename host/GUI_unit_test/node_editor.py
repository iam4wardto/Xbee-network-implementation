'''import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

show_demo()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()'''

import dearpygui.dearpygui as dpg

dpg.create_context()

# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)

# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    dpg.delete_item(app_data)

def main_maximize_callback(sender, app_data, user_data):
    print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")
    btn_label = dpg.get_item_label("btnMax")
    if btn_label == "Maximize":
        dpg.set_item_label("btnMax","Minimize")
        dpg.set_primary_window("winMain",True)
    else:
        dpg.set_item_label("btnMax", "Maximize")
        dpg.set_primary_window("winMain", False)

with dpg.window(label="Tutorial", width=400, height=400,tag="winMain"):

    dpg.add_text("Link denotes parent-child.", bullet=True)
    dpg.add_button(label="Maximize",tag="btnMax",callback=main_maximize_callback)
    with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, tracked=True):
        with dpg.node(label="Node 1"):
            with dpg.node_attribute(label="Node A1"):
                dpg.add_input_float(label="F1", width=150)

            with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(label="F2", width=150)

        with dpg.node(label="Node 2"):
            with dpg.node_attribute(label="Node A3"):
                dpg.add_input_float(label="F3", width=200)

            with dpg.node_attribute(label="Node A4", attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_input_float(label="F4", width=200)

dpg.add_viewport_menu_bar(label="viewport menu",tag="mainMenu")

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()