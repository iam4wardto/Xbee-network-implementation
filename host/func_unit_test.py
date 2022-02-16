import serial.tools.list_ports


com_list= serial.tools.list_ports.comports()
for port, desc, hwid in sorted(com_list):
        print("{}: {} [{}]".format(port, desc, hwid))