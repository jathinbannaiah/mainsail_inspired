import serial as sr
import serial.tools.list_ports
import threading

ACKNOWLEDGEMENT = True

class Serial_Class:
    def __init__(self, parent):
        self.parent = parent
        self.serial = sr.Serial()
        self.serial.baudrate = 115200  # Same baudrate has been used in tiva C code also
        self.serial.timeout = 3.0
        self.lock = threading.Lock()
    def connect(self):
        try:
            available_ports = list(sr.tools.list_ports.comports())
            for port in available_ports:
                if "In-Circuit Debug Interface" in port.description:  # Works for Linux systems, automatically detects the ports and connects
                    self.serial.port = port.device
                else:
                    self.serial.port = 'COM5'  # For windows purpose
            print(self.serial)
            # print("Port:", port.device)
            self.serial.open()
            if self.serial.is_open:
                print(self.serial.is_open)
                self.parent.tiva_status.setText("Tiva Online")
                self.parent.tiva_status.setStyleSheet("color: green")
        except:
                print("Unable to establish the serial connection")
                self.parent.printToConsole("Unable to establish the serial connection")
                self.parent.tiva_status.setText("Tiva Offline")
                self.parent.tiva_status.setStyleSheet("color: red")

    def readData(self):  # Function to receive the data from tiva ( multithreading is used)
        global ACKNOWLEDGEMENT
        while True:
            try:

                data = self.serial.read(500)  # To read 500 bytes of data
                data = data.decode('utf-8', errors='replace')

                if len(data) > 5:  # Because all the return statements length is greater than 5, used to avoid reading of garbage value
                    print("reading")
                    self.lock.acquire()               #Acquiring thread lock to implement synchronisation
                    AKNOWLEDGEMENT = True
                    self.lock.release()
                    self.parent.printToConsole(data)
                    print(data)
                    if "L1" in data:  # For limit switch purpose, L1 returned by Tiva when Limit switch 1 is clicked
                        self.parent.limitSwitchLeft.setText("Triggered")
                        self.parent.limitSwitchLeft.setStyleSheet("color: green")
                        self.parent.limitSwitchRight.setText("Open")
                        self.parent.limitSwitchRight.setStyleSheet("color: red")
                    if "L2" in data:  # L2 is returned when limit switch 2 is clicked
                        self.parent.limitSwitchLeft.setText("Open")
                        self.parent.limitSwitchLeft.setStyleSheet("color: red")
                        self.parent.limitSwitchRight.setText("Triggered")
                        self.parent.limitSwitchRight.setStyleSheet("color: green")
                        # self.printToConsole(data)
            except:
                print("Read loop error")

    def serial_write(self, command):  # Function to handle the serial write functionality to tiva
        global ACKNOWLEDGEMENT
        self.lock.acquire()
        ack = ACKNOWLEDGEMENT
        self.lock.release()
        try:
            if command == "Ready\r":
                self.serial.write(command.encode())

            elif ack:
                print(command)
                print("Writing")
                self.acknowledgement = False
                AKNOWLEDGEMENT = False
                self.serial.write(command.encode())
            else:
                print("Acknowledgement not received")
        except:
            print("Serial write error")





# def main():
#
#     window = Serial_Class()
#     window.connect()
#     window.readData()
#
#
# if __name__ == '__main__':
#     main()
