import pyautogui

class serial_param:
    PORT = ""
    BAUD_RATE = 115200


# adjust all gui params here...
class params:
    def __init__(self):
        pass

    hidpi = False
    if pyautogui.size()[0] > 3000:
        hidpi = True
    if hidpi:
        scale = 3
    else:
        scale = 1

    # size of three windows
    main_width = 900 * scale
    main_height = 600 * scale
    logger_width = 500 * scale
    logger_height = 250 * scale
    func_width = 500 * scale
    func_height = 350 * scale
    coord_pos = [20 * scale, 200 * scale]  # int coord pos in the node editor
    discovery_indicator_x_offset = 80 if hidpi == False else 200

    # windows position
    winExitConfirm_pos = [220 * scale, 180 * scale]
    winLog_pos = [400 * scale, 350 * scale]
    winFuncPanel_pos = [400 * scale, 0]
    winWelcome_pos = [250 * scale, 180 * scale]
    winStarted_pos = [50 * scale, 30 * scale]
    winLoadingIndicator_pos = [400 * scale, 200 * scale]

    # colors
    rgb_red = [255, 0, 0]
    rgb_green = [0, 255, 0]
    rgb_green2 = [255, 179, 13]
    rgb_white = [255, 255, 255]
    rgb_blue = [0,191,255]


# coordinator should be named COORD
# adjust all gui params here...
class network:
    def __init__(self):
        pass
    # network
    coord = None         # zigbee coordinator
    xbee_network = None  # class <XBeeNetwork>, represents an XBee Network
    nodes = None         # nodes discovered, list of <remoteXbeeDevice> object
    nodes_id = []        # nodes names, exclude coord
    available_nodes = []  # available nodes id, deal with node add and removal
    nodes_obj = []       # list of <node_container> object to save info
    connections = None   # link in the network
    NODE_ID = "NI"

    # logger
    log = None


class node_container:
    '''
    a wrapper for each node to cover all the info of the floodlight it represents
    '''
    def __init__(self,xbee_obj):
        self.node_xbee = xbee_obj
    # save get_...() response of each node
    node_xbee = None
    is_available = True   # node status, true when init
    temperature = "n/a"   # temperature, use string here
    rssi = float('-inf')  # rssi value foe each node
    led_color = []

    # status check
    handshake_time = None

# instantiate the <network> object
global net
net = network()