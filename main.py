#########################
# USB Border Patrol
# Main Script
#########################
# Dependency Imports
import usb.core, usb.util

##################

# check if there are two USB storage devices plugged in
def verify_usbs() -> bool:
    print('blah')
    busses = usb.busses()
    print(busses)
    for bus in busses:
        print(bus)

if __name__ == '__main__':
    # script has been triggered by a Linux subsystem
    # assume USB has been plugged in
    if verify_usbs():
        # we have verified that two USB storages devices have been connected
        # now, let's verify its files and copy them to the second USB
        print("test")
