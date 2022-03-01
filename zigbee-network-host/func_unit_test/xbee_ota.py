from digi.xbee.filesystem import FileSystemException,update_remote_filesystem_image
from digi.xbee.devices import XBeeDevice
from digi.xbee.exception import XBeeException
from digi.xbee.filesystem import LocalXBeeFileSystemManager

# TODO: Replace with the serial port where your local module is connected to.
PORT = "COM7"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 115200
# TODO: Replace with the name of the remote XBee to use. If empty, local is used.
REMOTE_NODE_ID = "ROUTER1"
# TODO: Replace with the XBee file system path to list its contents. Leave as 'None' to use '/flash'.
PATH_TO_LIST = None
ota_file_path = "../file_system_image.fs.ota"


def main():
    print(" +-------------------------------------------+")
    print(" | XBee Python Library List Directory Sample |")
    print(" +-------------------------------------------+\n")

    local_xbee = XBeeDevice(PORT, BAUD_RATE)
    fs_xbee = local_xbee

    try:
        local_xbee.open()

        if REMOTE_NODE_ID:
            # Obtain the remote XBee from the network.
            xbee_network = local_xbee.get_network()
            fs_xbee = xbee_network.discover_device(REMOTE_NODE_ID)
            if not fs_xbee:
                print("Could not find remote device '%s'" % REMOTE_NODE_ID)
                exit(1)

        filesystem_manager = fs_xbee.get_file_manager()
        #filesystem_manager.connect()
        #filesystem_manager.format_filesystem()

        #print(filesystem_manager.get_volume_info(timeout=20))

        update_remote_filesystem_image(fs_xbee, ota_filesystem_file=ota_file_path)
        '''
        path_to_list = PATH_TO_LIST
        if not path_to_list:
            path_to_list = "/flash"
        files = filesystem_manager.list_directory(path_to_list)
        print("Contents of '%s' (%s):\n" %
              (path_to_list, fs_xbee if fs_xbee.is_remote() else "local"))
        for file in files:
            print(file)'''

    except (XBeeException, FileSystemException) as e:
        print("ERROR: %s" % str(e))
        exit(1)
    finally:
        #filesystem_manager.disconnect()
        if local_xbee and local_xbee.is_open():
            local_xbee.close()



if __name__ == '__main__':
    main()