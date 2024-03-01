import serial as sr
import serial.tools.list_ports
available_ports = list(sr.tools.list_ports.comports())
for port in available_ports:
    print(port.description)
    if "In-Circuit Debug Interface" in port.description:  # Works for Linux systems, automatically detects the ports and connects
        serial.port = port.device
        print("yes")

    else:
        serial.port = 'COM5'  # For windows purpose
print(serial)
