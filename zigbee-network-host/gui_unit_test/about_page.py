import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

from dearpygui_ext.logger import mvLogger

# Include the following code before showing the viewport/calling `dearpygui.dearpygui.show_viewport`.
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    pass


dpg.create_context()
with dpg.font_registry():
    font = dpg.add_font("../font/OpenSans-Regular.ttf", 15*3, tag="sans-font")
dpg.bind_font("sans-font")
dpg.set_global_font_scale(1)
dpg.create_viewport()

def menuAbout_callback():
    dpg.show_item(winMenuAbout)

with dpg.theme(tag="themeWinBgBlack"):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [0,0,0],category=dpg.mvThemeCat_Core)

width, height, channels, data = dpg.load_image("../figure/floodlight.png")

with dpg.texture_registry():
    texture_id_1 = dpg.add_static_texture(width, height, data)

with dpg.window(label="test", width=800, height=800, pos=(100, 100), tag="__demo_id"):
    with dpg.menu_bar():
        with dpg.menu(label="Tools"):
            dpg.add_menu_item(label="Show About", callback=lambda: dpg.show_tool(dpg.mvTool_About))
            dpg.add_menu_item(label="Show Metrics", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
            dpg.add_menu_item(label="Show Documentation", callback=lambda: dpg.show_tool(dpg.mvTool_Doc))
            dpg.add_menu_item(label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug))
            dpg.add_menu_item(label="Show Style Editor", callback=lambda: dpg.show_tool(dpg.mvTool_Style))
            dpg.add_menu_item(label="Show Font Manager", callback=lambda: dpg.show_tool(dpg.mvTool_Font))
            dpg.add_menu_item(label="Show Item Registry", callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))

        with dpg.menu(label="Settings"):
            dpg.add_menu_item(label="Getting Started", check=True, callback=lambda s, a: dpg.configure_app(wait_for_input=a))
            dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda: dpg.toggle_viewport_fullscreen())
            dpg.add_menu_item(label="About", check=True, callback=menuAbout_callback)


with dpg.window(label="About Semester Project", autosize=True, modal=False, show=False,
                no_background=False, no_close=False) as winMenuAbout:
    dpg.add_text("Implementing Distributed Network Communication for Outdoor Sensor Network")
    dpg.add_text("Author: Yue Li")
    dpg.add_text("Teammate: Cedric Weibel")
    dpg.add_text("Supervisor: Hendrik Kolvenbach, Konrad Meyer")
    dpg.add_image(texture_id_1)

dpg.bind_item_theme(winMenuAbout, "themeWinBgBlack")




# main loop
dpg.show_viewport()
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()