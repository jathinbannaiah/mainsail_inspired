from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
import requests
import sys
import Serial_file
#import serial.tools.list_ports
import threading
import multiprocessing
import time
from hopper import Hopper
from environment import Environment
from Z import Zmotion
from Serial_file import Serial_Class

RECOATER_RPM = 100
ROLLER_RPM = 100
MOTOR_DIR = False
RMOTOR_DIR = False


class GUI(QMainWindow):

    def __init__(self):
        try:
            super(GUI, self).__init__()
            self.MainWindow = uic.loadUi("27Oct(Ganesh).ui", self)
            self.environment_instance = Environment(self)
            self.hopper = Hopper(self)  # Hopper class instance
            self.Z_instance = Zmotion()  # Z class instance
            self.serial = Serial_Class(self)

            # API initialisation
            self.api = "192.168.137.11"
            self.params = {"apikey": 'B508534ED20348F090B4D0AD637D3660'}

            # RECOATER SYSTEM INITIALISATION

            # self.serial = serial.Serial()
            # self.serial.baudrate = 115200  # Same baudrate has been used in tiva C code also
            # self.serial.timeout = 3.0
            self.lock = threading.Lock()  # Lock variable, for synchronisation purpose
            self.acknowledgement = True
            self.semaphore = multiprocessing.Semaphore(1)
            self.pause_flag = multiprocessing.Value('b', False)  # Creating a shared variable

            # try:
            #     available_ports = list(serial.tools.list_ports.comports())
            #     for port in available_ports:
            #         if "In-Circuit Debug Interface" in port.description:  # Works for Linux systems, automatically detects the ports and connects
            #             self.serial.port = port.device
            #         else:
            #             self.serial.port = 'COM5'  # For windows purpose
            #     print(self.serial)
            #     # print("Port:", port.device)
            #     self.serial.open()
            #     if self.serial.is_open:
            #         print(self.serial.is_open)
            #         self.tiva_status.setText("Tiva Online")
            #         self.tiva_status.setStyleSheet("color: green")

            #Calling connect function
            self.serial.connect()

            # Start a separate thread for reading and displaying serial data
            self.read_thread = threading.Thread(target=self.serial.readData)
            self.read_thread.daemon = True
            self.read_thread.start()

            # Start a separate thread for refreshing the temperature screen
            self.environment_thread = threading.Thread(target=self.environment_control)
            self.environment_thread.daemon = True
            self.environment_thread.start()


            # print("sending reset signal")
            # cmd = "RESET\r"
            # print(f"Command:{cmd}")
            # self.serial.write(cmd.encode())
            # buffer = self.serial.read(100)
            # print(buffer)

            # while True:
            #     print("Checking for readiness")
            #     cmd = "READY\r"
            #     print(f"Command:{cmd}")
            #     self.serial.write(cmd.encode())
            #     buffer = self.serial.read(100)
            #     print(buffer)
            #     if buffer == "Ready":
            #         print("Tiva ready for operation")
            #         break

            # except:
            #     print("Unable to establish the serial connection")
            #     self.printToConsole("Unable to establish the serial connection")
            #     self.tiva_status.setText("Tiva Offline")
            #     self.tiva_status.setStyleSheet("color: red")

            # UI widgets initialisation
            self.start_process.released.connect(self.start_thread)  # Use lambda when you have to pass arguments
            self.stop_process.released.connect(self.stop_thread)
            self.pause.released.connect(self.pause_auto_process)

            self.home.released.connect(
                self.Home_recoater)  # .released signifies after the mouse click is released call the function
            self.recoater_Estop.released.connect(self.recoater_emergency)

            self.recoaterRPM.returnPressed.connect(lambda: self.RPM(True, 0))
            self.rollerRPM.returnPressed.connect(lambda: self.RPM(False, 0))

            self.changeDIR.released.connect(lambda: self.changeDirection(True))
            self.decStop.released.connect(lambda: self.deceleratingStop(True))
            # self.instStop.clicked.connect(lambda: self.instantStop(True))
            self.brake.released.connect(lambda: self.Brake(True))
            self.recoater.released.connect(lambda: self.start(True))

            self.RchangeDIR.released.connect(lambda: self.changeDirection(False))
            self.RdecStop.released.connect(lambda: self.deceleratingStop(False))
            # self.RinstStop.clicked.connect(lambda: self.instantStop(False))
            self.Rbrake.released.connect(lambda: self.Brake(False))
            self.roller.released.connect(lambda: self.start(False))

            self.R5.released.connect(lambda: self.RPM(True, 5))
            self.R10.released.connect(lambda: self.RPM(True, 10))
            self.R100.released.connect(lambda: self.RPM(True, 100))
            self.mR5.released.connect(lambda: self.RPM(True, -5))
            self.mR10.released.connect(lambda: self.RPM(True, -10))
            self.mR100.released.connect(lambda: self.RPM(True, -100))

            self.RO5.released.connect(lambda: self.RPM(False, 5))
            self.RO10.released.connect(lambda: self.RPM(False, 10))
            self.RO100.released.connect(lambda: self.RPM(False, 100))
            self.mRO5.released.connect(lambda: self.RPM(False, -5))
            self.mRO10.released.connect(lambda: self.RPM(False, -10))
            self.mRO100.released.connect(lambda: self.RPM(False, -100))

            # Hopper buttons initialisation
            self.Lhopper.released.connect(lambda: self.hopper.select("L"))
            self.Rhopper.released.connect(lambda: self.hopper.select("R"))
            self.Hopper1sec.released.connect(lambda: self.hopper.timeSelect(1))
            self.Hopper3sec.released.connect(lambda: self.hopper.timeSelect(3))
            self.Hopper5sec.released.connect(lambda: self.hopper.timeSelect(5))
            self.Hopper1mm.released.connect(lambda: self.hopper.openingSelect(1))
            self.Hopper5mm.released.connect(lambda: self.hopper.openingSelect(5))
            self.Hopper10mm.released.connect(lambda: self.hopper.openingSelect(10))
            self.Hopper_Dose.released.connect(lambda: self.hopper.Dose(self.api, self.params))

            # Z system buttons initialisation
            self.Zaxis_up.released.connect(lambda: self.Z_instance.self.Zaxis_up)
            self.Zaxis_down.released.connect(lambda: self.Z_instance.self.Zaxis_down)
            self.Zstage_up.released.connect(self.Z_instance.Z_Up)
            self.Zstage_down.released.connect(self.Z_instance.Z_Down)
            self.Z1.released.connect(lambda: self.Z_instance.set_distance(1))
            self.Z10.released.connect(lambda: self.Z_instance.set_distance(10))
            self.Z100.released.connect(lambda: self.Z_instance.set_distance(100))
            # self.Z1.released.connect(lambda: self.Z_instance.set_distance(1))

            # Temperature Buttons
            self.C1_ok.released.connect(lambda: self.environment_instance.set_target_temperature("C1"))
            self.C2_ok.released.connect(lambda: self.environment_instance.set_target_temperature("C2"))
            self.C3_ok.released.connect(lambda: self.environment_instance.set_target_temperature("C3"))
            self.B1_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B1"))
            self.B2_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B2"))
            self.HopL_ok.released.connect(lambda: self.environment_instance.set_target_temperature("Lhopper"))
            self.HopR_ok.released.connect(lambda: self.environment_instance.set_target_temperature("Rhopper"))

            # Button click effect
            self.start_process.pressed.connect(
                lambda: self.ButtonClickEffect(self.start_process))  # Use lambda when you have to pass arguments
            self.stop_process.pressed.connect(lambda: self.ButtonClickEffect(self.stop_process))
            self.pause.pressed.connect(lambda: self.ButtonClickEffect(self.pause))

            self.home.pressed.connect(lambda: self.ButtonClickEffect(self.home))
            self.recoater_Estop.pressed.connect(lambda: self.ButtonClickEffect(self.recoater_Estop))

            self.changeDIR.pressed.connect(lambda: self.ButtonClickEffect(self.changeDIR))
            self.decStop.pressed.connect(lambda: self.ButtonClickEffect(self.decStop))
            # self.instStop.clicked.connect(lambda: self.instantStop(True))
            self.brake.pressed.connect(lambda: self.ButtonClickEffect(self.brake))
            self.recoater.pressed.connect(lambda: self.ButtonClickEffect(self.recoater))

            self.RchangeDIR.pressed.connect(lambda: self.ButtonClickEffect(self.RchangeDIR))
            self.RdecStop.pressed.connect(lambda: self.ButtonClickEffect(self.RdecStop))
            # self.RinstStop.clicked.connect(lambda: self.instantStop(False))
            self.Rbrake.pressed.connect(lambda: self.ButtonClickEffect(self.Rbrake))
            self.roller.pressed.connect(lambda: self.ButtonClickEffect(self.roller))

            self.R5.pressed.connect(lambda: self.ButtonClickEffect(self.R5))
            self.R10.pressed.connect(lambda: self.ButtonClickEffect(self.R10))
            self.R100.pressed.connect(lambda: self.ButtonClickEffect(self.R100))
            self.mR5.pressed.connect(lambda: self.ButtonClickEffect(self.mR5))
            self.mR10.pressed.connect(lambda: self.ButtonClickEffect(self.mR10))
            self.mR100.pressed.connect(lambda: self.ButtonClickEffect(self.mR100))

            self.RO5.pressed.connect(lambda: self.ButtonClickEffect(self.RO5))
            self.RO10.pressed.connect(lambda: self.ButtonClickEffect(self.RO10))
            self.RO100.pressed.connect(lambda: self.ButtonClickEffect(self.RO100))
            self.mRO5.pressed.connect(lambda: self.ButtonClickEffect(self.mRO5))
            self.mRO10.pressed.connect(lambda: self.ButtonClickEffect(self.mRO10))
            self.mRO100.pressed.connect(lambda: self.ButtonClickEffect(self.mRO100))

            # Temperature Buttons
            self.C1_ok.clicked.connect(lambda: self.environment_instance.set_target_temperature("C1"))
            self.C2_ok.clicked.connect(lambda: self.environment_instance.set_target_temperature("C2"))
            self.C3_ok.clicked.connect(lambda: self.environment_instance.set_target_temperature("C3"))
            self.B1_ok.clicked.connect(lambda: self.environment_instance.set_target_temperature("B1"))
            self.B2_ok.clicked.connect(lambda: self.environment_instance.set_target_temperature("B2"))
            self.HopL_ok.clicked.connect(lambda: self.environment_instance.set_target_temperature("Lhopper"))
            self.HopR_ok.clicked.connect(lambda: self.environment_instance.set_target_temperature("Rhopper"))

            self.show()

        except:
            print("Program initialisation failed")
            self.printToConsole("Program initialisation failed")

    def ButtonClickEffect(self, object):
        self.current_style = object.styleSheet()  # Obtaining current style sheet
        # print(self.current_style)
        new_style = ""
        current_style = self.current_style
        for line in current_style.split(';'):  # Checking for background-color line
            if line.strip().startswith("background"):
                # print(line)
                line = line.split(":")
                line[1] = line[1].strip()
                rgb = line[1][4:len(line[1]) - 1].split(",")
                # print(rgb)
                red = int(rgb[0])
                green = int(rgb[1])
                blue = int(rgb[2])
                # print(red,green,blue)
                new_red = red + 30  # Modifying the colors to genereate click effect
                new_green = green + 30
                new_blue = blue + 30
                if new_red > 255:
                    new_red = 255
                elif new_green > 255:
                    new_green = 255
                elif new_blue > 255:
                    new_blue = 255
                break
            else:
                # print(line)
                new_style = new_style + line + ";"
        new_color = f"\nbackground-color: rgb({new_red}, {new_green}, {new_blue});"
        new_style = current_style + new_color
        # print(new_style)
        # print(new_style)
        object.setStyleSheet(new_style)  # applying the new stylesheet

    def pause_auto_process(self):  # Function to pause the automation loop
        self.pause.setStyleSheet(self.current_style)
        with self.semaphore:  # Acquiring the semaphore
            if self.pause_flag.value == True:
                self.pause_flag.value = False
                self.pause.setText("PAUSE")
                # self.printToConsole("PAUSE")
            else:
                self.pause_flag.value = True
                self.pause.setText("RESUME")
                # self.printToConsole("RESUME")

    def start_thread(self):  # Function to initialise and start the automation loop
        self.start_process.setStyleSheet(self.current_style)
        # Disabling all the buttons and line edit widgets before starting automation process
        self.recoaterRPM.setEnabled(False)  # Disabling all buttons and widgets when the automation loop is running
        self.rollerRPM.setEnabled(False)
        self.home.setEnabled(False)
        self.changeDIR.setEnabled(False)
        self.decStop.setEnabled(False)
        # self.instStop.clicked.connect(lambda: self.instantStop(True))
        self.brake.setEnabled(False)
        self.recoater.setEnabled(False)

        self.RchangeDIR.setEnabled(False)
        self.RdecStop.setEnabled(False)
        # self.RinstStop.clicked.connect(lambda: self.instantStop(False))
        self.Rbrake.setEnabled(False)
        self.roller.setEnabled(False)

        self.R5.setEnabled(False)
        self.R10.setEnabled(False)
        self.R100.setEnabled(False)
        self.mR5.setEnabled(False)
        self.mR10.setEnabled(False)
        self.mR100.setEnabled(False)

        self.RO5.setEnabled(False)
        self.RO10.setEnabled(False)
        self.RO100.setEnabled(False)
        self.mRO5.setEnabled(False)
        self.mRO10.setEnabled(False)
        self.mRO100.setEnabled(False)

        self.Lhopper.setEnabled(False)
        self.Rhopper.setEnabled(False)
        self.Hopper1sec.setEnabled(False)
        self.Hopper3sec.setEnabled(False)
        self.Hopper5sec.setEnabled(False)
        self.Hopper1mm.setEnabled(False)
        self.Hopper5mm.setEnabled(False)
        self.Hopper10mm.setEnabled(False)
        self.Hopper_Dose.setEnabled(False)

        # Creating a separate process for automation
        self.auto_process = multiprocessing.Process(target=self.start_process_function)
        self.auto_process.daemon = True
        self.auto_process.start()

    def stop_thread(self):  # Fucntion to  handle the stoppage of the automation loop
        self.stop_process.setStyleSheet(self.current_style)
        try:
            self.auto_process.terminate()
        except:
            print("No process is running")
        time.sleep(1)
        self.Brake(True)
        time.sleep(1)
        self.Brake(False)
        # Enabling all the buttons and line edit widgets before starting automation process
        self.recoaterRPM.setEnabled(True)
        self.rollerRPM.setEnabled(True)
        self.home.setEnabled(True)
        self.changeDIR.setEnabled(True)
        self.decStop.setEnabled(True)
        # self.instStop.clicked.connect(lambda: self.instantStop(True))
        self.brake.setEnabled(True)
        self.recoater.setEnabled(True)

        self.RchangeDIR.setEnabled(True)
        self.RdecStop.setEnabled(True)
        # self.RinstStop.clicked.connect(lambda: self.instantStop(False))
        self.Rbrake.setEnabled(True)
        self.roller.setEnabled(True)

        self.R5.setEnabled(True)
        self.R10.setEnabled(True)
        self.R100.setEnabled(True)
        self.mR5.setEnabled(True)
        self.mR10.setEnabled(True)
        self.mR100.setEnabled(True)

        self.RO5.setEnabled(True)
        self.RO10.setEnabled(True)
        self.RO100.setEnabled(True)
        self.mRO5.setEnabled(True)
        self.mRO10.setEnabled(True)
        self.mRO100.setEnabled(True)

        self.Lhopper.setEnabled(True)
        self.Rhopper.setEnabled(True)
        self.Hopper1sec.setEnabled(True)
        self.Hopper3sec.setEnabled(True)
        self.Hopper5sec.setEnabled(True)
        self.Hopper1mm.setEnabled(True)
        self.Hopper5mm.setEnabled(True)
        self.Hopper10mm.setEnabled(True)
        self.Hopper_Dose.setEnabled(True)

    # def serial_write(self, command):  # Function to handle the serial write functionality to tiva
    #     try:
    #         self.serial.write(command.encode())
    #     except:
    #         print("Serial write error")

    def start_process_function(self):  # Function to handle the automation loop
        try:
            cmd = "Ready\r"  # Dummy command to the tiva board. Tiva board does not react
            self.serial.serial_write(cmd)
            time.sleep(1)

            hopper_cmdL = {
                "command": "move_hopper_left"
            }

            hopper_cmdR = {
                "command": "move_hopper_right"
            }

            # Setting RPM of Recoater motors
            self.RPM(False, 1)
            time.sleep(1)
            self.RPM(True, 1)
            time.sleep(1)

            # Home Z axis
            # home_z = {
            #     "command": ""
            # }
            # try:
            #     req = requests.post(url=f"http://{self.api}/api/printer/command", params=self.params, json=home_z, timeout=5)
            #     req.raise_for_status()
            # except requests.exceptions.Timeout:
            #     print("Home Z Request timed out. Connection could not be established.")
            #     #self.printToConsole("Hopper Request timed out. Connection could not be established.")
            # except requests.exceptions.RequestException as e:
            #     print(f"A Z request error occurred: {e}")
            #     #self.printToConsole(f"An Hopper request error occurred: {e}"

            # Homming Recoater System
            print("First")
            self.changeDirection(False)

            time.sleep(1)

            self.changeDirection(True)

            time.sleep(8)
            # cmd = "R FW\r"
            # # self.printToConsole(f"Command:{cmd}")
            # self.serial.serial_write(cmd)
            # # self.waitforResponse()
            # time.sleep(1)
            #
            # cmd = "FW\r"
            # # self.printToConsole(f"Command:{cmd}")
            # self.serial.serial_write(cmd)
            # # self.waitforResponse()

            time.sleep(8)

            print("Second")
            self.changeDirection(False)

            time.sleep(1)

            self.changeDirection(True)

            time.sleep(8)

            hopper_cmd = hopper_cmdL

            while True:  # auotmation loop. order to operation = Z -> Hopper -> Recoater
                try:
                    if self.pause_flag.value == True:
                        time.sleep(1)
                    else:
                        # Move Z axis
                        move_z = {
                            "command": ""
                        }

                        # Open Hopper
                        try:
                            print("Opening Hopper")
                            req = requests.post(url=f"http://{self.api}/api/printer/command", params=self.params,
                                                json=hopper_cmd, timeout=5)
                            req.raise_for_status()
                            if hopper_cmd == hopper_cmdL:
                                hopper_cmd = hopper_cmdR
                            elif hopper_cmd == hopper_cmdR:
                                hopper_cmd = hopper_cmdL
                            else:
                                print("Hopper command change error")
                                # self.printToConsole("Hopper command change error")
                        except requests.exceptions.Timeout:
                            print("Hopper Request timed out. Connection could not be established.")
                            # self.printToConsole("Hopper Request timed out. Connection could not be established.")
                        except requests.exceptions.RequestException as e:
                            print(f"An Hopper request error occurred: {e}")
                            # self.printToConsole(f"An Hopper request error occurred: {e}")

                        time.sleep(3)

                        # Move Recoater
                        print("Third")
                        self.changeDirection(False)
                        time.sleep(1)
                        self.changeDirection(True)
                        time.sleep(8)

                        try:
                            print("Moving z")
                            req = requests.post(url=f"http://{self.api}/api/printer/command", params=self.params,
                                                json=move_z, timeout=5)
                            req.raise_for_status()
                        except requests.exceptions.Timeout:
                            print("Move Z Request timed out. Connection could not be established.")
                            # self.printToConsole("Hopper Request timed out. Connection could not be established.")
                        except requests.exceptions.RequestException as e:
                            print(f"A Z request error occurred: {e}")
                            # self.printToConsole(f"An Hopper request error occurred: {e}"
                        time.sleep(5)

                except:
                    print("Loop error")
                    # self.printToConsole("Loop error")
                    continue
        except:
            print("Auto process error")
            # self.printToConsole("Auto process error")

    def environment_control(self):  # Function to handle the environment management process
        self.environment_instance.update_screen()

    def Home_recoater(self):  # Function to home the recoater system
        self.home.setStyleSheet(self.current_style)
        # self.printToConsole("Homing recoater system")
        try:
            cmd = "RV\r"
            # self.printToConsole(f"Command:{cmd}")
            self.serial.serial_write(cmd)
            # self.waitforResponse()
            # time.sleep(15)
        except:
            print("Homing error")

    def recoater_emergency(self):  # Function to handing the emergency stoppage of the recoater system
        self.recoater_Estop.setStyleSheet(self.current_style)
        try:
            cmd = "STOP IN\r"
            self.serial.serial_write(cmd)

            time.sleep(1)

            cmd = "R STOP IN\r"
            self.serial.serial_write(cmd)
        except:
            print("Recoater emergerncy stop errror")

    # def readData(self):  # Function to receive the data from tiva ( multithreading is used)
    #     while True:
    #         data = self.serial.read(500)  # To read 500 bytes of data
    #         data = data.decode('utf-8', errors='replace')
    #         print(data)
    #         if len(data) > 5:  # Because all the return statements length is greater than 5, used to avoid reading of garbage value
    #             # print("read")
    #             self.printToConsole(data)
    #             print(data)
    #             if "L1" in data:  # For limit switch purpose, L1 returned by Tiva when Limit switch 1 is clicked
    #                 self.limitSwitchLeft.setText("Triggered")
    #                 self.limitSwitchLeft.setStyleSheet("color: green")
    #                 self.limitSwitchRight.setText("Open")
    #                 self.limitSwitchRight.setStyleSheet("color: red")
    #             if "L2" in data:  # L2 is returned when limit switch 2 is clicked
    #                 self.limitSwitchLeft.setText("Open")
    #                 self.limitSwitchLeft.setStyleSheet("color: red")
    #                 self.limitSwitchRight.setText("Triggered")
    #                 self.limitSwitchRight.setStyleSheet("color: green")
    #                 # self.printToConsole(data)

    def printToConsole(self, text):  # Function to print the console in the UI
        # Add text to the console
        self.console.append("AMCOE/system/console$" + text)

    def RPM(self, rpm, num):  # Function to set the RPM to the motors in the recoater system
        try:
            global RECOATER_RPM
            global ROLLER_RPM
            if rpm == True and num == 0:  # When RPM is set using line edit widget, i.e entering the value for MOTOR 1
                val = self.recoaterRPM.text()
                if val.isdigit():
                    val = int(val)
                    RECOATER_RPM = val
                    print(f"new recoater rpm: {RECOATER_RPM}")
                    # self.printToConsole(f"new recoater rpm: {RECOATER_RPM}")
                    if val < 40 or val > 3150:
                        print("Please enter valid inputs")
                        # self.printToConsole("Please enter valid inputs")
                    else:
                        if self.serial.serial.is_open:
                            cmd = "RPM" + f" {RECOATER_RPM}\r"
                            print(f"Command:{cmd}")
                            # self.printToConsole(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            # self.waitforResponse()
                            # buffer = self.serial.read(100)
                            # buffer = buffer.decode('utf-8')
                            # print(buffer)
                            # self.printToConsole(buffer)
                        else:
                            print("Serial port is not open")
                            # self.printToConsole("Serial port is not open")

                else:
                    print("Please enter valid inputs")
                    # self.printToConsole("Please enter valid inputs")
            elif rpm == False and num == 0:  # Setting rpm for motor 2 by direct entry
                val = self.rollerRPM.text()
                if val.isdigit():
                    val = int(val)
                    ROLLER_RPM = val
                    print(f"new roller rpm: {ROLLER_RPM}")
                    # self.printToConsole(f"new roller rpm: {ROLLER_RPM}")
                    if val < 40 or val > 3150:
                        print("Please enter valid inputs")
                        # self.printToConsole("Please enter valid inputs")
                    else:
                        if self.serial.serial.is_open:
                            cmd = "rpm" + f" {ROLLER_RPM}\r"
                            print(f"Command:{cmd}")
                            # self.printToConsole(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            # self.waitforResponse()
                        # buffer = self.serial.read(100)
                        # print(buffer)
                        # buffer = buffer.decode('utf-8')
                        # self.printToConsole(buffer)
                        else:
                            print("Serial port is not open")
                        # self.printToConsole("Serial port is not open")

                else:
                    print("Please enter valid inputs")
                    # self.printToConsole("Please enter valid inputs")
            elif rpm == True and num != 0:  # Changing RPM of motor 1 by clicking one of the given buttons
                if num == 5:
                    self.R5.setStyleSheet(self.current_style)
                elif num == 10:
                    self.R10.setStyleSheet(self.current_style)
                elif num == 100:
                    self.R100.setStyleSheet(self.current_style)
                elif num == -5:
                    self.mR5.setStyleSheet(self.current_style)
                elif num == -10:
                    self.mR10.setStyleSheet(self.current_style)
                elif num == -100:
                    self.mR100.setStyleSheet(self.current_style)
                RECOATER_RPM = RECOATER_RPM + num
                if self.serial.serial.is_open:
                    cmd = "RPM" + f" {RECOATER_RPM}\r"
                    print(f"Command:{cmd}")
                    # self.printToConsole(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                    # self.waitforResponse()
                    # buffer = self.serial.read(100)
                    # buffer = buffer.decode('utf-8')
                    # print(buffer)
                    # self.printToConsole(buffer)
                else:
                    print("Serial port is not open")
                    # self.printToConsole("Serial port is not open")

            else:  # Changing the RPM of motor 2 by clicking one the given buttons
                if num == 5:
                    self.RO5.setStyleSheet(self.current_style)
                elif num == 10:
                    self.RO10.setStyleSheet(self.current_style)
                elif num == 100:
                    self.RO100.setStyleSheet(self.current_style)
                elif num == -5:
                    self.mRO5.setStyleSheet(self.current_style)
                elif num == -10:
                    self.mRO10.setStyleSheet(self.current_style)
                elif num == -100:
                    self.mRO100.setStyleSheet(self.current_style)
                ROLLER_RPM = ROLLER_RPM + num
                if self.serial.serial.is_open:
                    cmd = "rpm" + f" {ROLLER_RPM}\r"
                    print(f"Command:{cmd}")
                    # self.printToConsole(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                    # self.waitforResponse()
                    # buffer = self.serial.read(100)
                    # print(buffer)
                    # buffer = buffer.decode('utf-8')
                    # self.printToConsole(buffer)
                else:
                    print("Serial port is not open")
                    # self.printToConsole("Serial port is not open")
        except:
            print("Error")
            # self.printToConsole("Error")
            # print("Trying to open new serial port")
            # try:
            #     self.serial.open()
            # except:
            #     print("unable to establish serial communication")

    def start(self, motor_select):  # Function to handle the start of the motors
        try:
            if motor_select:  # Motor 1
                self.recoater.setStyleSheet(
                    self.current_style)  # this type of line in all functions is used for the click effect
                if self.serial.serial.is_open:
                    cmd = "START\r"
                    print(f"Command:{cmd}")
                    # self.printToConsole(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                    # self.waitforResponse()
                    # buffer = self.serial.read(100)
                    # buffer = buffer.decode('utf-8')
                    # print(buffer)
                    # self.printToConsole(buffer)
                else:
                    print("Serial port is not open")
                    # self.printToConsole("Serial port is not open")

            else:  # Motor 2
                self.roller.setStyleSheet(self.current_style)
                if self.serial.serial.is_open:
                    cmd = "R START\r"
                    print(f"Command:{cmd}")
                    # self.printToConsole(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                    # self.waitforResponse()
                    # buffer = self.serial.read(100)
                    # print(buffer)
                    # buffer = buffer.decode('utf-8')
                    # self.printToConsole(buffer)
                else:
                    print("Serial port is not open")
                    # self.printToConsole("Serial port is not open")

        except:
            print("Error")
            # self.printToConsole("Error")
            print("Trying to open new serial port")
            # self.printToConsole("Trying to open new serial port")
            try:
                self.serial.open()
            except:
                print("unable to establish serial communication")
                # self.printToConsole("unable to establish serial communication")

    def Brake(self, motor_select):  # Function to handle the breaking of recoater motors
        if motor_select:
            self.brake.setStyleSheet(self.current_style)
        else:
            self.Rbrake.setStyleSheet(self.current_style)

        try:
            if self.serial.serial.is_open:
                if motor_select:
                    self.brake.setStyleSheet(self.current_style)
                    try:
                        cmd = "BRAKE\r"
                        print(f"Command:{cmd}")
                        # self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                        # self.waitforResponse()
                        # buffer = self.serial.read(100)
                        # print(buffer)
                        # buffer = buffer.decode('utf-8')
                        # self.printToConsole(buffer)
                    except:
                        print("Error in braking Motor 1")
                        # self.printToConsole("Error in braking Motor 1")
                else:
                    self.Rbrake.setStyleSheet(self.current_style)  # R prefix indicated motor 2 / ROLLER
                    try:
                        cmd = "R BRAKE\r"
                        print(f"Command:{cmd}")
                        # self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                        # self.waitforResponse()
                        # buffer = self.serial.read(100)
                        # print(buffer)
                        # buffer = buffer.decode('utf-8')
                        # self.printToConsole(buffer)
                    except:
                        print("Error in braking R Motor")
                        # self.printToConsole("Error in braking R Motor")

            else:
                print("Unable to detect a serial connection")
                # self.printToConsole("Unable to detect a serial connection")

        except:
            print("Error in brake function")
            # self.printToConsole("Error in brake function")

    def instantStop(self,
                    motor_select):  # Function to instantaneously stop the motor, the buttons are not displayed in the GUI
        try:
            if self.serial.serial.is_open:
                if motor_select:
                    try:
                        cmd = "STOP IN\r"
                        print(f"Command:{cmd}")
                        # self.printToConsole(f"COMMAND:{cmd}")
                        self.serial.serial_write(cmd)
                        # self.waitforResponse()
                    # buffer = self.serial.read(100)
                    # print(buffer)
                    # buffer = buffer.decode('utf-8')
                    # self.printToConsole(buffer)
                    except:
                        print("Error in INSTANTANEOUSLY braking Motor 1")
                        # self.printToConsole("Error in INSTANTANEOUSLY braking Motor 1")
                else:
                    try:
                        cmd = "R STOP IN\r"
                        print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                        # self.waitforResponse()
                        # buffer = self.serial.read(100)
                        # print(buffer)
                        # buffer = buffer.decode('utf-8')
                        # self.printToConsole(buffer)
                    except:
                        print("Error in INSTANTANEOUSLY braking R Motor")
                        # self.printToConsole("Error in INSTANTANEOUSLY braking R Motor")

            else:
                print("Unable to detect a serial connection")
                # self.printToConsole("Unable to detect a serial connection")

        except:
            print("Error in instant brake function")
            # self.printToConsole("Error in instant brake function")

    def deceleratingStop(self, motor_select):  # To stop the motors without a jerk
        if motor_select:
            self.decStop.setStyleSheet(self.current_style)
        else:
            self.RdecStop.setStyleSheet(self.current_style)
        try:
            if self.serial.serial.is_open:
                if motor_select:
                    self.decStop.setStyleSheet(self.current_style)
                    try:
                        cmd = "STOP DC\r"
                        print(f"Command:{cmd}")
                        # self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                        # self.waitforResponse()
                        # buffer = self.serial.read(100)
                        # print(buffer)
                        # buffer = buffer.decode('utf-8')
                        # self.printToConsole(buffer)
                    except:
                        print("Error in DECELERATING brakes in Motor 1")
                        # self.printToConsole("Error in DECELERATING brakes in Motor 1")
                else:
                    self.RdecStop.setStyleSheet(self.current_style)
                    try:
                        cmd = "R STOP DC\r"
                        print(f"Command:{cmd}")
                        # self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                        # self.waitforResponse()
                        # buffer = self.serial.read(100)
                        # print(buffer)
                        # buffer = buffer.decode('utf-8')
                        # self.printToConsole(buffer)
                    except:
                        print("Error in DECELERATING brakes in R Motor")
                    # self.printToConsole("Error in DECELERATING brakes in R Motor")

            else:
                print("Unable to detect a serial connection")
                # self.printToConsole("Unable to detect a serial connection")

        except:
            print("Error in decelerating brake function")
            # self.printToConsole("Error in decelerating brake function")

    def changeDirection(self, motor_select):  # Function to handle the change of direction of motion of recoater motors
        if motor_select:
            self.changeDIR.setStyleSheet(self.current_style)
        else:
            self.RchangeDIR.setStyleSheet(self.current_style)

        try:
            global MOTOR_DIR
            global RMOTOR_DIR
            if self.serial.serial.is_open:
                if motor_select:
                    self.changeDIR.setStyleSheet(self.current_style)
                    try:
                        if MOTOR_DIR:  # Variable to store the direction of motion
                            cmd = "RV\r"
                            print(f"Command:{cmd}")
                            # self.printToConsole(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            # self.waitforResponse()
                            # buffer = self.serial.read(100)
                            # print(buffer)
                            # buffer = buffer.decode('utf-8')
                            # self.printToConsole(buffer)
                            MOTOR_DIR = False
                            self.changeDIR.setText("Move Right")
                        else:
                            cmd = "FW\r"
                            print(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            # self.waitforResponse()
                            # buffer = self.serial.read(100)
                            # print(buffer)
                            # buffer = buffer.decode('utf-8')
                            # self.printToConsole(buffer)
                            MOTOR_DIR = True
                            self.changeDIR.setText("Move left")
                    except:
                        print("Error in changing direction of roation of Motor 1")
                        # self.printToConsole("Error in changing direction of roation of Motor 1")

                else:
                    self.RchangeDIR.setStyleSheet(self.current_style)
                    try:
                        if RMOTOR_DIR:
                            cmd = "R RV\r"
                            print(f"Command:{cmd}")
                            # self.printToConsole(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            # self.waitforResponse()
                            # buffer = self.serial.read(100)
                            # print(buffer)
                            # buffer = buffer.decode('utf-8')
                            # self.printToConsole(buffer)
                            RMOTOR_DIR = False
                            self.RchangeDIR.setText("AntiClockwise")
                        else:
                            cmd = "R FW\r"
                            print(f"Command:{cmd}")
                            # self.printToConsole(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            # self.waitforResponse()
                            # buffer = self.serial.read(100)
                            # print(buffer)
                            # buffer = buffer.decode('utf-8')
                            # self.printToConsole(buffer)
                            RMOTOR_DIR = True
                            self.RchangeDIR.setText("Clockwise")
                    except:
                        print("Error in changing direction of roation of Motor 1")
                        self.printToConsole("Error in changing direction of roation of Motor 1")
            else:
                print("Serial port not open")
                # self.printToConsole("Serial port not open")

        except:
            print("Error in the direction changing function")
            # self.printToConsole("Error in the direction changing function")


def main():
    app = QApplication([])
    window = GUI()
    app.exec_()


if __name__ == '__main__':
    main()
