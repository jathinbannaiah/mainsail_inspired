import serial as sr
import serial.tools.list_ports
import threading
import multiprocessing
import sys
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QPushButton
import platform
from PyQt5.QtGui import QTextCursor
# from PyQt5.QtCore import  QMetaType
# # Register QTextCursor as a metatype
# QMetaType.registerType(QTextCursor)



ACKNOWLEDGEMENT = True

class Serial_Class(QObject):
    Console_data = pyqtSignal(dict)
    Serial_console_data = pyqtSignal(dict)
    def __init__(self, parent):
        try:
            super().__init__()
            self.parent = parent
            self.serial = sr.Serial()
            self.serial.baudrate = 115200  # Same baudrate has been used in tiva C code also
            self.serial.timeout = 1.0
            self.lock = multiprocessing.Lock()
            self.ack = True
            self.read_conn, self.write_conn = multiprocessing.Pipe()
        except Exception as e:
            self.parent.parent_connection.send(f"Error S1: Error in Seiral_file.__init__()\n{e}")
    def connect(self):
        try:
            available_ports = list(sr.tools.list_ports.comports())
            for port in available_ports:
                if platform.system() in ["Linux"]:
                    if "In-Circuit Debug Interface" in port.description:  # Works for Linux systems, automatically detects the ports and connects
                        self.serial.port = port.device
                    elif "USB-Serial Controller" in port.description:
                        self.serial.port = port.device
                else:
                    if "Stellaris Virtual Serial Port" in port.description:      #In different windows, it shows up differently
                        self.serial.port = port.device  # For windows purpose
            print(self.serial)
            # print("Port:", port.device)
            self.serial.open()
            if self.serial.is_open:
                print(self.serial.is_open)
                #Resetting tiva
                self.serial_write("reset\r")
                self.Console_data.emit({"Tiva": "Online"})              #To modify the GUI
        except Exception as e:
                print(f"Unable to establish the serial connection\n{e}")
                #self.parent.parent_connection.send(f"Error S2: Error in Seiral_file.connect()\n{e}")
                #self.parent.printToConsole("Unable to establish the serial connection")
                # self.parent.tiva_status.setText("Tiva Offline")
                # self.parent.tiva_status.setStyleSheet("color: red")
                self.Console_data.emit({"Tiva": "Offline","Error":f"Error S2: Error in Seiral_file.connect()\n{e}"})

    def readData(self, connection, scanner_connection):  # Function to receive the data from tiva ( multithreading is used)
        self.connection = connection
        self.scanner_connection = scanner_connection
        while True:
            try:
                if self.connection.poll():                      #Polling to check if data is available to read, it returns True if data is present on the pipe
                    received_data = self.connection.recv()     #Anything to be written on the console is sent here to avoid threading and multiprocessign errors
                    print(f"Received data: {received_data}")    #But it is bad to update GUi from secondary threads
                    if "Error" in received_data:
                        self.Console_data.emit({"error": received_data})
                    else:
                    #self.parent.printToConsole(received_data)
                        self.Console_data.emit({"data": received_data})
                else:
                    if self.parent.debug_var == 2:
                        pass
                        #print("Multithreading pipe empty")

            except Exception as e:
                print(f"Print to console error\n{e}")
                self.Console_data.emit({"Error": f"Error S3: Error in Seiral_file.readData()\n{e}"})

            try:

                data = self.serial.read(500)  # To read 500 bytes of data
                data = data.decode('utf-8', errors='replace')
                if "OK_scanner" in data:                                    #For scanner but Ok is not a good acknowledgement
                    print("Condition met")
                    self.parent.scanner_parent_conn.send("Ok\r\n")

                if len(data) > 1:  # Because all the return statements length is greater than 5, used to avoid reading of garbage value
                    print(f"reading: {data}")
                    self.read_conn.send("True")        #Sending acknowledgement to write function
                    #self.parent.printToSerialMonitor(data)
                    self.Serial_console_data.emit({"data":data})
                    if "Ex" in data or " L1" in data or "L2" in data:        #Also, to account for non-linear motion of recoater               #Because recoater sends ok instantly but will be in loop and will send Ex.. after the loop
                        self.connection.send(data)        #For waitforResponse program
                    # if self.parent.debug_var == 2:
                    #     print(data)
                    if "L1" in data:  # For limit switch purpose, L1 returned by Tiva when Limit switch 1 is clicked
                        self.Serial_console_data.emit({"L1":"Triggered","L2":"Open"})              #For serial monitor not console
                        # self.parent.limitSwitchLeft.setText("Triggered")
                        # self.parent.limitSwitchLeft.setStyleSheet("color: green")
                        # self.parent.limitSwitchRight.setText("Open")
                        # self.parent.limitSwitchRight.setStyleSheet("color: red")
                    if "L2" in data:  # L2 is returned when limit switch 2 is clicked
                        self.Serial_console_data.emit({"L2":"Triggered","L1":"Open"})
                        # self.parent.limitSwitchLeft.setText("Open")
                        # self.parent.limitSwitchLeft.setStyleSheet("color: red")
                        # self.parent.limitSwitchRight.setText("Triggered")
                        # self.parent.limitSwitchRight.setStyleSheet("color: green")
                        # self.printToConsole(data)
            except Exception as e:
                pass
                print(f"Read loop error\n{e}")


    def serial_write(self, command):  # Function to handle the serial write functionality to tiva
        try:
            if command == "Ready\r" or command == "reset\r" or command == "gpio_reset\r":
                self.parent.parent_connection.send(f"{command[:len(command)-2]} Signal")
                self.serial.write(command.encode())
                return
            elif self.write_conn.poll():         # USing multiprocessing pipe, becuase using class varialbe or gloabal variable was causing scope issues
                self.ack = self.write_conn.recv()

            if self.ack:
                if self.parent.debug_var == 2:
                    #print(command)
                    print("Writing")
                    #self.parent.printToConsole(f"Writing command: {command}")
                self.serial.write(command.encode())
                self.ack = False
            else:
                if self.parent.debug_var == 2:
                    print("Acknowledgement not received")
                    self.parent.parent_connection.send(f"Error S4: Error in Seiral_file.serial_write()(Acknowledgement)")
        except Exception as e:
            print(f"Serial write error\n{e}")
            self.parent.parent_connection.send(f"Error S5: Error in Seiral_file.serial_write()\n{e}")

    def test_function(self, event):
        print("Hello, I am under the water, Please help me")

class SerialMonitor(QDialog):
    def __init__(self):
        super().__init__()
        print("Openning serial monitor")
        self.setWindowTitle("Serial Monitor")
        self.setGeometry(200,200,300,200)

        self.label = QLabel("Serial Monitor")
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)








# def main():
#
#     window = Serial_Class()
#     window.connect()
#     window.readData()
#
#
# if __name__ == '__main__':
#     main()
