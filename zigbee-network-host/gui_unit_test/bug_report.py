import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.theme() as themeWinBgBlack:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [0,0,0])

with dpg.window(label="About", modal=False) as winMenuAbout:
    dpg.add_text("test")

dpg.bind_item_theme(winMenuAbout, themeWinBgBlack)

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()