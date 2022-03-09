'''import dearpygui.dearpygui as dpg

dpg.create_context()

width, height, channels, data = dpg.load_image("../figure/somefile.jpg")

with dpg.texture_registry(show=True):
    dpg.add_static_texture(width, height, data, tag="texture_tag")

with dpg.window(label="Tutorial"):
    #dpg.add_image("texture_tag")
    dpg.add_file_dialog(label="test_file")


dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()'''

'''
import dearpygui.dearpygui as dpg
dpg.create_context()

def callback(sender, app_data):
    print("Sender: ", sender)
    print("App Data: ", app_data)

with dpg.file_dialog(directory_selector=False, show=False, callback=callback, file_count=3, id="file_dialog_id"):
    dpg.add_file_extension(".*", color=(255, 255, 255, 255))
    dpg.add_file_extension(".cpp", color=(255, 255, 0, 255))
    dpg.add_file_extension(".h", color=(255, 0, 255, 255))
    dpg.add_file_extension(".py", color=(0, 255, 0, 255))
    dpg.add_button(label="fancy file dialog")

with dpg.window(label="Tutorial", width=800, height=300):
    dpg.add_button(label="File Selector", callback=lambda: dpg.show_item("file_dialog_id"))

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()'''

import dearpygui.dearpygui as dpg

dpg.create_context()

def callback(sender, app_data):
    print("Sender: ", sender)
    print("App Data: ", app_data)


with dpg.file_dialog(show=False, directory_selector=False, tag="file_dialog_tag",
                     callback=callback, file_count=2,height=200):
    dpg.add_file_extension(".py")


with dpg.window(label="Tutorial", width=400, height=300):
    dpg.add_button(label="File Selector", callback=lambda: dpg.show_item("file_dialog_tag"))

dpg.create_viewport( width=400, height=300)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()


