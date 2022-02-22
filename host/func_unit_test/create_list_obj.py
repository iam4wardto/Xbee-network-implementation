from net_cfg import *

nodes_id = ["ROUTER1","router2"]

node_objects = {name: node_container() for name in nodes_id}
for name, obj in node_objects.items():
    globals()[name] = obj
print(ROUTER1) # use explicit name to reference node is OK, BUT not general!
print("construct OK")