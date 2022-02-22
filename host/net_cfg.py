
# coordinator should be named COORD
# adjust all gui params here...
class network:
    def __init__(self):
        pass
    # network
    coord = None         # zigbee coordinator
    xbee_network = None  # network object
    nodes = None         # nodes discovered
    connections = None   # link in the network
    NODE_ID = "NI"

    # logger
    log = None

global net
net = network()