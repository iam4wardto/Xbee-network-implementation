# importing modules
import urllib.request
from PIL import Image
import dearpygui.dearpygui as dpg

map_url = "https://maps.googleapis.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY" \
          "&zoom=13&size=600x400" \
          "&maptype=roadmap" \
          "&map_id=c0881174066edcec" \
          "&markers=color:blue%7Clabel:1%7C40.702147,-74.015794" \
          "&markers=color:green%7Clabel:2%7C40.711614,-74.012318" \
          "&markers=color:red%7Clabel:3%7C40.718217,-73.998284" \
          "&key=AIzaSyBlLnKa2csTpSt1gdlyg-j_dYkEg_F9wlc"

urllib.request.urlretrieve(map_url,"map.png")
width0, height0, channels0, data0 = dpg.load_image("map.png")
print(width0,height0)

img = Image.open("map.png")
img.show()
