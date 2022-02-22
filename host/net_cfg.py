
# coordinator should be named COORD
# adjust all gui params here...
class network:
    def __init__(self):
        pass
    # network
    coord = None         # zigbee coordinator
    xbee_network = None  # network object
    nodes = None         # nodes discovered, list of xbee library object
    nodes_id = []        # nodes names, exclude coord
    nodes_obj = []       # list of node_container object to save info
    connections = None   # link in the network
    NODE_ID = "NI"

    # logger
    log = None

class node_container:
    def __init__(self,xbee_obj):
        self.node_xbee = xbee_obj
    # save get_...() response of each node
    node_xbee = None
    temperature = "n/a" # temperature, use string here
    led_color = []

global net
net = network()