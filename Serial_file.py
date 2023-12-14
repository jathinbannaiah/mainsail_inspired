import serial as sr
import serial.tools.list_ports
import threading
import multiprocessing
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QTextCursor
# from PyQt5.QtCore import  QMetaType
#
#
# # Register QTextCursor as a metatype
# QMetaType.registerType(QTextCursor)

# Now you can use QTextCursor in signal-slot connections


ACKNOWLEDGEMENT = True

class Serial_Class:
    def __init__(self, parent):
        self.parent = parent
        self.serial = sr.Serial()
        self.serial.baudrate = 115200  # Same baudrate has been used in tiva C code also
        self.serial.timeout = 1.0
        self.lock = multiprocessing.Lock()
        self.ack = True
        self.read_conn, self.write_conn = multiprocessing.Pipe()
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
        except Exception as e:
                print(f"Unable to establish the serial connection\n{e}")
                #self.parent.printToConsole("Unable to establish the serial connection")
                self.parent.tiva_status.setText("Tiva Offline")
                self.parent.tiva_status.setStyleSheet("color: red")

    def readData(self, connection):  # Function to receive the data from tiva ( multithreading is used)
        self.connection = connection
        while True:
            try:
                if self.connection.poll():                      #Polling to check if data is available to read, it returns True if data is present on the pipe
                    received_data = self.connection.recv()
                    print(f"Received data {received_data}")
                    self.parent.printToConsole(received_data)
                else:
                    if self.parent.debug_var == 2:
                        pass
                        #print("Multithreading pipe empty")
            except Exception as e:
                print(f"Print to console error\n{e}")

            try:

                data = self.serial.read(500)  # To read 500 bytes of data
                data = data.decode('utf-8', errors='replace')

                if len(data) > 5:  # Because all the return statements length is greater than 5, used to avoid reading of garbage value
                    print(f"reading: {data}")
                    self.read_conn.send("True")
                    self.parent.printToSerialMonitor(data)
                    # if self.parent.debug_var == 2:
                    #     print(data)
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
            except Exception as e:
                print(f"Read loop error\n{e}")


    def serial_write(self, command):  # Function to handle the serial write functionality to tiva
        try:
            if command == "Ready\r":
                self.parent.parent_connection.send("Ready Signal")
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
                    self.parent.parent_connection.send("Acknowledgement not received")
        except Exception as e:
            print(f"Serial write error\n{e}")
            self.parent.parent_connection.send(f"Serial write error\n{e}")

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
