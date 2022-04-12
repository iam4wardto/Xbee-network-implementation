This project develops a host user interface for the meshed network of sensor-equipped illumination devices, which can be used in disaster site illumination and mark points of interest in exploration.  

<img src="https://user-images.githubusercontent.com/32224259/163026186-fbffa709-121b-4591-890d-65075dc7096a.png" height="220" /> <img src="https://user-images.githubusercontent.com/32224259/163024570-afcf8989-92f9-4d45-9b29-5cc3cc735c40.jpg" height="220" /> <img src="https://user-images.githubusercontent.com/32224259/163026505-580f1969-362d-4dfa-b1c5-a5bd4a796556.png" height="220" />

**The meshed network supports:**
- Network with up to 100+ nodes
- Individual control and broadcasting
- Collect sensor data from nodes
- Grouping nodes and commands together
- Error checking and return transmit status

## User Interface
The user interface is devided into 3 subwindows. On the left, we have **main windows** including menu, node graph view and node list view. On top right, it's the **function panel**, where related commands are grouped together and put into each tab. On bottom right, we have **logger windows** showing infos, errors, network modifications and transmit status.

<img src="https://user-images.githubusercontent.com/32224259/163027115-757c20b0-af5f-4048-af51-cee2a1b22492.jpg" height="450" > 

## Main Features
The comprehensive GUI enables all the functionality within the network, includes graph view, network request, stauts check, new node discovery and source routing.
### Device Control
The brightness, color and light patterns of end devices can be set. GPS, temperature and acceleration values are collected and sent to host. It's convenient to set up cyclic tasks to get device information automatically.
### Source Routing
Defined by network protocol, when direct communications between two nodes are not available, the message will pass through several realy nodes before reaching the destination. Source routing will return the exact path connecting sender and receiver. We can lighten up this path by command.
### Sync Clock
Depend on the actual network connection, the latency to each node in the network is different. In latency-sensitive use cases, such as aligning light patterns, we need to synchronize the clocks of the end devices. 
### Connection Check
The node connection is constantly checked inside the network, if a node is offline, it is shown on the graph view and a notification will be sent to logger. When this node is back online, the status also refreshes. This connection check also applies to new node, when a new node that is not discovered occurs, it it saved in the network and plotted onto the grapgh view. 
### OTA Update
The settings and code on zigbee modules can be updated without connecting them locally.This is done by selecting a system image and transmit it to remote node.
### Test Mode
There is test tool integrated in the user interface for latency test and payload test. The test mode should be enabled in the menu and a single node must be chosen for the test.

## Network Requirement
| Hardware | Software |
| ------ | ------ |
| ESP32 | deployed code |
| XBee3 ZigBee Module | code in micropython |
| Host PC | `host_gui.py` | 

_Note: code running on end devices is not included in this repo._

