from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt5 import uic
import requests
import threading
import multiprocessing
import time
from hopper import Hopper
from environment import Environment
from Z import Zmotion
from Serial_file import Serial_Class
from timing import Time
from cli_file_handling import Marking_Data
from automation import Automation
import time
import numpy as np
import pyqtgraph as pg
import testing_process as test
from scancard import ScanCard

RECOATER_RPM = 50
ROLLER_RPM = 50
MOTOR_DIR = False
RMOTOR_DIR = False
PITCH = 30
GEAR_RATIO = 30
FAST_RPM_DISTANCE = 450
SLOW_RPM_DISTANCE = 70
FAST_RPM = 120
SLOW_RPM = 15
RED = QTextCharFormat()
RED.setForeground(QColor("red"))
GREEN = QTextCharFormat()
GREEN.setForeground(QColor(0, 200, 0))

R_Commands = ["Roller_FW", "Roller_RV", "Roller_STOP_IN", "Roller_STOP_DC", "Roller_START", "Roller_RUN_FW",
              "Roller_RUN_RV", "Roller_BRAKE", "Roller_RPM", "Recoater_FW", "Recoater_RV", "Recoater_STOP_IN",
              "Recoater_STOP_DC", "Recoater_START", "Recoater_RUN_FW", "Recoater_RUN_RV", "Recoater_BRAKE",
              "Recoater_Go_Left", "Recoater_Go_Right", "Recoater_RPM","reset","gpio_reset"]

H_Commands = ["move_hopper_right","move_hopper_left"]

Z_Commands = [""]



class GUI(QMainWindow, QObject):
    mainwindow_console_signal = pyqtSignal(str)

    def __init__(self, parent_conn, child_conn, scanner_parent_conn, scanner_child_conn):
        try:
            super(GUI, self).__init__()
            self.MainWindow = uic.loadUi("27Oct(Ganesh).ui", self)

            # Temperature module initialisation
            self.environment_instance = Environment(self)
            self.C1_target.setText("")
            self.C2_target.setText("")
            self.B3_target.setText("")
            self.B1_target.setText("")
            self.B2_target.setText("")
            self.HopL_target.setText("")
            self.HopR_target.setText("")

            self.hopper = Hopper(self)  # Hopper class instance
            self.Z_instance = Zmotion(self)  # Z class instance
            self.serial = Serial_Class(self)
            self.time_instant = Time(self)
            self.cli_file_object = Marking_Data(self)
            self.scancard = ScanCard()

            # Scanner connection objects initialisation
            self.scanner_parent_conn = scanner_parent_conn
            self.scanner_child_conn = scanner_child_conn
            # self.auto_process = Automation(self)
            # self.temperatures = {}
            self.file_path = ""
            self.WFR_previous_data = ""

            self.debug_var = 1
            self.homming = False                              #To check whether the recoater home button is clicked or not and hence call the reverse function to reach home

            self.parent_connection = parent_conn

            #Dynamic Command Entry lines
            self.Command_input.returnPressed.connect(self.dynamic_commands)

            #Temperature plot initialisation
            self.chamber_plot = self.graphWidget.plot(pen='g',name="Chamber")
            self.bed_plot = self.graphWidget.plot(pen='b',name="Bed")
            temp_temp = [ 50,100,200,300,20,14,34,25,12,53]
            temp_time = [5,10,15,20,25,30,35,40,45,50]
            self.chamber_plot.setData(temp_time,temp_temp)
            self.bed_plot.setData(temp_temp,temp_time)



            # Console write signal definition
            self.Z_instance.console_sig.connect(self.printToConsole)
            self.hopper.console_signal.connect(self.printToConsole)
            self.mainwindow_console_signal.connect(self.printToConsole)
            # self.auto_process.automation_console_signal.connect(self.printToConsole)

            # UI pages initialisation
            self.dashboard.clicked.connect(lambda: self.page_change("dashboard"))
            self.thermal.clicked.connect(lambda: self.page_change("thermal"))
            self.cli_file.clicked.connect(lambda: self.page_change("cli_file"))

            # API initialisation
            self.api = "172.19.253.103"
            self.params = {"apikey": 'B508534ED20348F090B4D0AD637D3660'}

            self.lock = threading.Lock()  # Lock variable, for synchronisation purpose
            self.acknowledgement = True
            self.semaphore = multiprocessing.Semaphore(1)
            self.pause_flag = multiprocessing.Value('b', False)  # Creating a shared variable

            # Calling connect function
            self.serial.connect()


            # Start a separate thread for reading and displaying serial data
            self.read_thread = threading.Thread(target=self.serial.readData,
                                                args=(child_conn, self.scanner_parent_conn))
            self.read_thread.daemon = True
            self.read_thread.start()
            self.serial.Console_data.connect(self.printToConsole)
            self.serial.Serial_console_data.connect(self.printToSerialMonitor)

            # Start a separate thread for refreshing the temperature screen
            self.thread = QThread()
            self.environment_instance.moveToThread(self.thread)
            self.environment_instance.status_signal.connect(self.update_gui_temp)
            self.thread.started.connect(self.environment_instance.run)
            self.thread.start()             #Automatically calls the run function in environment.py

            # self.environment_thread = threading.Thread(target=self.environment_control)
            # self.environment_thread.daemon = True
            # self.environment_thread.start()             #QTextCursor error is spwaned here  #Not really, mostly time related not caused by lines
            # self.timer = QTimer(self)
            # self.timer.timeout.connect(self.update_gui_temp)
            # self.timer.start(3000)

            # UI widgets initialisation
            self.start_process.released.connect(self.start_thread)  # Use lambda when you have to pass arguments
            self.stop_process.released.connect(self.stop_thread)
            self.pause.released.connect(self.pause_auto_process)

            #Scancard drawing buttons
            self.draw_triangle.released.connect(self.scancard.draw_triangle_)
            self.draw_square.released.connect(self.scancard.draw_square_)
            self.set_speed.released.connect(self.change_scanner_speed)
            self.draw_square2.released.connect(self.scancard.draw_square2_)
            self.hatch_square2.released.connect(self.scancard.hatch_square2_)
            self.stop_marking.released.connect(self.scancard.stop_marking)
            self.halt_marking.released.connect(self.scancard.halt_marking)
            self.continue_marking.released.connect(self.scancard.continue_marking)
            self.jump_xyz.released.connect(self.JumpToXYZ)
            self.mark_xyz.released.connect(self.MarkToXYZ)

            self.jump_xyz.pressed.connect(lambda: self.ButtonClickEffect(self.jump_xyz))
            self.mark_xyz.pressed.connect(lambda: self.ButtonClickEffect(self.mark_xyz))

            #Effect, not enabled because idk why but I don't want to import main to scancard.py
            # self.stop_marking.pressed.connect(lambda: self.ButtonClickEffect(self.stop_marking))
            # self.halt_marking.pressed.connect(lambda: self.ButtonClickEffect(self.halt_marking))
            # self.continue_marking.pressed.connect(lambda: self.ButtonClickEffect(self.continue_marking))

            # CLI file widgets
            self.browse_files.released.connect(self.open_file_dialog)
            self.OK_file_select.released.connect(self.cli_final_select)
            self.get_point.released.connect(self.get_next_coordinates)
            self.start_print.setEnabled(False)
            self.stop_print.setEnabled(False)
            self.stop_print.released.connect(self.stop_scanning_operation)
            self.start_print.released.connect(self.cli_file_object.initialise_print)

            # Debug level selector
            self.DebugLevel.activated.connect(self.Select_debug_level)

            #Testing function
            self.test.released.connect(self.testing_function)

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
            self.set_attributes.released.connect(self.R_motion_attributes)

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
            self.Zaxis_up.released.connect(self.Z_instance.Zaxis_move_up)
            self.Zaxis_down.released.connect(self.Z_instance.Zaxis_move_down)
            self.Zstage_up.released.connect(self.Z_instance.Z_Up)
            self.Zstage_down.released.connect(self.Z_instance.Z_Down)
            self.Z1.released.connect(lambda: self.Z_instance.set_distance(1))
            self.Z10.released.connect(lambda: self.Z_instance.set_distance(10))
            self.Z100.released.connect(lambda: self.Z_instance.set_distance(100))
            # self.Z1.released.connect(lambda: self.Z_instance.set_distance(1))

            # Temperature Buttons
            self.C1_ok.released.connect(lambda: self.environment_instance.set_target_temperature("C1"))
            self.C2_ok.released.connect(lambda: self.environment_instance.set_target_temperature("C2"))
            self.B1_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B1"))
            self.B2_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B2"))
            self.B3_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B3"))
            self.B4_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B4"))
            self.B5_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B5"))
            self.B6_ok.released.connect(lambda: self.environment_instance.set_target_temperature("B6"))
            self.HopL_ok.released.connect(lambda: self.environment_instance.set_target_temperature("Lhopper"))
            self.HopR_ok.released.connect(lambda: self.environment_instance.set_target_temperature("Rhopper"))

            # # Button click effect
            # self.start_process.pressed.connect(
            #     lambda: self.ButtonClickEffect(self.start_process))  # Use lambda when you have to pass arguments
            # self.stop_process.pressed.connect(lambda: self.ButtonClickEffect(self.stop_process))
            # self.pause.pressed.connect(lambda: self.ButtonClickEffect(self.pause))

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
            self.set_attributes.pressed.connect(lambda: self.ButtonClickEffect(self.set_attributes))

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

            self.Zaxis_up.pressed.connect(lambda: self.ButtonClickEffect(self.Zaxis_up))
            self.Zaxis_down.pressed.connect(lambda: self.ButtonClickEffect(self.Zaxis_down))
            self.Zstage_up.pressed.connect(lambda: self.ButtonClickEffect(self.Zstage_up))
            self.Zstage_down.pressed.connect(lambda: self.ButtonClickEffect(self.Zstage_down))
            self.Z1.pressed.connect(lambda: self.ButtonClickEffect(self.Z1))
            self.Z10.pressed.connect(lambda: self.ButtonClickEffect(self.Z10))
            self.Z100.pressed.connect(lambda: self.ButtonClickEffect(self.Z100))

            self.Lhopper.pressed.connect(lambda: self.ButtonClickEffect(self.Lhopper))
            self.Rhopper.pressed.connect(lambda: self.ButtonClickEffect(self.Rhopper))
            self.Hopper1sec.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper1sec))
            self.Hopper3sec.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper3sec))
            self.Hopper5sec.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper5sec))
            self.Hopper1mm.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper1mm))
            self.Hopper5mm.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper5mm))
            self.Hopper10mm.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper10mm))
            self.Hopper_Dose.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper_Dose))

            # Temperature Buttons
            self.C1_ok.pressed.connect(lambda: self.ButtonClickEffect(self.C1_ok))
            self.C2_ok.pressed.connect(lambda: self.ButtonClickEffect(self.C2_ok))
            self.B1_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B1_ok))
            self.B2_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B2_ok))
            self.B3_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B3_ok))
            self.B4_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B4_ok))
            self.B5_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B5_ok))
            self.B6_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B6_ok))
            self.HopL_ok.pressed.connect(lambda: self.ButtonClickEffect(self.HopL_ok))
            self.HopR_ok.pressed.connect(lambda: self.ButtonClickEffect(self.HopR_ok))

            #Testing
            self.test.pressed.connect(lambda: self.ButtonClickEffect(self.test))


            # CLI file buttons
            self.browse_files.pressed.connect(lambda: self.ButtonClickEffect(self.browse_files))
            self.OK_file_select.pressed.connect(lambda: self.ButtonClickEffect(self.OK_file_select))
            self.get_point.pressed.connect(lambda: self.ButtonClickEffect(self.get_point))
            self.stop_print.pressed.connect(lambda: self.ButtonClickEffect(self.stop_print))
            self.start_print.pressed.connect(lambda: self.ButtonClickEffect(self.start_print))

            # Timer to update log
            self.log_timer = QTimer(self)
            self.log_timer.timeout.connect(self.rotate_log)

            self.show()

        except Exception as e:
            print(f"Program initialisation failed with error: {e}")
            self.parent_connection.send(f"Error M1: Program initialisation failed with error\n{e}")

    def JumpToXYZ(self):
        try:
            self.jump_xyz.setStyleSheet(self.current_style)
        except Exception as e:
            print(str(e))
        try:
            x = int(self.scan_x.text())
            y = int(self.scan_y.text())
            z = int(self.scan_z.text())

            if x == "" or y == "" or z == "":
                print("Please provide x,y and z values")
            elif x < 0 or x > 67108863 or y < 0 or y > 67108863 or z < 0 or z > 67108863:
                print("Please provide values in the range (0,67108863)")
            else:
                cmd_ = self.scancard.make_command(x,y,z,"jump")
                self.scancard.send_command(cmd_)

        except Exception as e:
            print(str(e))

    def MarkToXYZ(self):
        try:
            self.mark_xyz.setStyleSheet(self.current_style)
        except Exception as e:
            print(str(e))
        try:
            x = int(self.scan_x.text())
            y = int(self.scan_y.text())
            z = int(self.scan_z.text())

            if x == "" or y == "" or z == "":
                print("Please provide x,y and z values")
            elif x < 0 or x > 67108863 or y < 0 or y > 67108863 or z < 0 or z > 67108863:
                print("Please provide values in the range (0,67108863)")
            else:
                cmd_ = self.scancard.make_command(x,y,z,"mark")
                self.scancard.send_command(cmd_)

        except Exception as e:
            print(str(e))





    def testing_function(self):
        test_thread = threading.Thread(target = test.testing_p,args = (self,))
        test_thread.daemon = True
        test_thread.start()

    def change_scanner_speed(self):
        markspeed = self.markspeed.text()
        jumpspeed = self.jumpspeed.text()

        if isinstance(markspeed,int) and isinstance(jumpspeed,int):
            self.scancard.change_speed(markspeed,jumpspeed)
        elif not isinstance(markspeed,int):
            print("Invalid markspeed value")
            self.scancard.change_speed(jumpS = markspeed)
        elif not isinstance(jumpspeed,int):
            print("Invalid jumpspeed value")
            self.scancard.change_speed(markS = markspeed)
        else:
            print("Invalid values")
            self.scancard.change_speed()
    def rotate_log(self):
        pass

    def RwaitforResponse(self):
        while True:
            if self.parent_connection.poll():
                received = self.parent_connection.recv()
                if "L1" in received or "L2" in received or "Ex17" in received or "Ex18" in received:  # Logic to find the end of non linear motion of recoater
                    # print("Enabling the recoater buttons")
                    self.R_enable_buttons()
                    break
            else:
                continue

    def waitforResponse(self,req = None):
        while True:
           if not self.parent_connection.poll():
                continue
           else:
                received = self.parent_connection.recv()
                if req == None:
                    print("Acknowledgement received:", received)
                    break
                elif received in req:
                    print("Acknowledgement received:", received)
                    break
                else:
                    pass

    def waitforPause(self):
        if self.pause_flag.value == True:
            while True:
                with self.semaphore:
                    if self.pause_flag.value == False:
                        break

    def stop_scanning_operation(self):
        self.stop_print.setStyleSheet(self.current_style)
        self.scanner_parent_conn.send("finish")

    def open_file_dialog(self):
        self.browse_files.setStyleSheet(self.current_style)
        try:
            options = QFileDialog.Options()
            file_dialog = QFileDialog()
            self.file_path, _ = file_dialog.getOpenFileName(self, "Select File", "",
                                                            "All Files (*);;Text Files (*.txt)", options=options)

            if self.file_path:
                self.file_entry.setText(self.file_path)
        except Exception as e:
            print(e)
            self.parent_connection.send(f"Error M2: Error in open_file_dialog()\n{e}")

    def cli_final_select(self):
        self.OK_file_select.setStyleSheet(self.current_style)
        try:
            self.file_path = self.file_entry.text()
            if self.file_path:
                self.cli_file_object.get_file(self.file_path)
                print(self.file_path)

            if not self.cli_file_object.checkForErrors():
                self.cli_file_object.generate_data()
        except Exception as e:
            # print(e)
            self.parent_connection.send(f"Error M3: Error in cli_final_select()\n{e}")

    def get_next_coordinates(self):
        self.get_point.setStyleSheet(self.current_style)
        try:
            if self.cli_file_object is not None:
                point = self.cli_file_object.get_next_pair()
                if point == "H/P complete":
                    self.point_display.setText("H/P finsihed")
                elif point == "Layer complete":
                    self.point_display.setText("Layer finsihed")
                else:
                    point = "(" + str(point[0]) + "," + str(point[1]) + ")" + "," + f"unit: {self.cli_file_object.unit}"
                    print(point)
                    self.point_display.setText(point)


        except Exception as e:
            print(e)
            self.parent_connection.send(f"Error M3: Error in get_next_coordinates()\n{e}")

    def page_change(self, page):
        try:
            if page == "dashboard":
                self.stackedWidget.setCurrentIndex(0)
                self.thermal_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,);")
                self.dashboard_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,0);")
                self.cli_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,);")
            elif page == "thermal":
                self.stackedWidget.setCurrentIndex(1)
                self.dashboard_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,);")
                self.thermal_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,0);")
                self.cli_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,);")
            elif page == "cli_file":
                self.stackedWidget.setCurrentIndex(2)
                self.dashboard_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,);")
                self.thermal_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,);")
                self.cli_select.setStyleSheet("border: 0px;\n background-color:rgb(255,255,0);")
        except Exception as e:
            self.parent_connection.send(f"Error M4: Error in page_change()\n{e}")

    def Select_debug_level(self):
        try:
            self.debug_var = int(self.DebugLevel.currentText())
            print("Debug level changed to ", self.debug_var)
            self.parent_connection.send(f"Debug level changed to {self.debug_var}")
        except Exception as e:
            self.parent_connection.send(f"Error M5: Error in Select_debug_level()\n{e}")

    def ButtonClickEffect(self, object):
        # Emergency recoater stop button click effect is very minute because of the extreme difference between the R,G and B values; initial (255,0,0), after (255,30,30) ;Not much difference
        try:
            self.current_style = object.styleSheet()  # Obtaining current style sheet
            new_style = ""
            current_style = self.current_style
            # print("curr",current_style)
            for line in current_style.split(';'):  # Checking for background-color line
                if line.strip().startswith("background"):
                    line = line.split(":")
                    line[1] = line[1].strip()
                    rgb = line[1][4:len(line[1]) - 1].split(",")
                    # print(rgb)
                    red = int(rgb[0])
                    green = int(rgb[1])
                    try:
                        blue = int(rgb[2])  # is causing errors for transparent buttons
                    except IndexError as e:
                        blue = " "
                    except ValueError as e:
                        blue = " "
                    new_red = red + 30  # Modifying the colors to genereate click effect
                    new_green = green + 30
                    if blue == " ":
                        new_blue = " "
                    else:
                        new_blue = blue + 30
                    try:
                        if new_red > 255:
                            new_red = 255
                        if new_green > 255:
                            new_green = 255
                        if new_blue > 255:
                            new_blue = 255
                    except:
                        new_blue = " "
                    break
                else:
                    new_style = new_style + line + ";"
            new_color = f"\nbackground-color: rgb({new_red}, {new_green}, {new_blue});"
            # print("col",new_color)
            new_style = current_style + new_color           #If i put new_style =new_style + new_color then the color values keeps on increasing in hopper module
            # print("style",new_style)
            object.setStyleSheet(new_style)  # applying the new stylesheet
        except Exception as e:
            print(f"Button click animation failed with error\n {e}")
            self.parent_connection.send(f"Error M6: Error in ButtonClickEffect()\n{e}")

    def pause_auto_process(self):  # Function to pause the automation loop
        try:
            self.pause.setStyleSheet(self.current_style)
            with self.semaphore:  # Acquiring the semaphore
                if self.pause_flag.value == True:
                    self.pause_flag.value = False
                    self.pause.setText("PAUSE")
                    self.time_instant.resumeTimer()
                    self.parent_connection.send("Process resumed")
                else:
                    self.pause_flag.value = True
                    self.pause.setText("RESUME")
                    self.time_instant.stopTimer()
                    self.parent_connection.send("Process will be paused after current cycle")
        except Exception as e:
            self.parent_connection.send(f"Error M7: Error in pause_auto_process()\n{e}")

    def start_thread(self):  # Function to initialise and start the automation loop
        try:
            self.start_process.setStyleSheet(self.current_style)
            with self.semaphore:  # Acquiring the semaphore
                self.pause_flag.value = False
                self.pause.setText("PAUSE")
            # Disabling all the buttons and line edit widgets before starting automation process
            self.start_process.setEnabled(False)
            self.recoaterRPM.setEnabled(False)
            self.rollerRPM.setEnabled(False)
            self.home.setEnabled(False)
            self.changeDIR.setEnabled(False)
            self.decStop.setEnabled(False)
            self.brake.setEnabled(False)
            self.recoater.setEnabled(False)
            self.set_attributes.setEnabled(False)

            self.RchangeDIR.setEnabled(False)
            self.RdecStop.setEnabled(False)
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

            self.Zaxis_up.setEnabled(False)
            self.Zaxis_down.setEnabled(False)
            self.Zstage_up.setEnabled(False)
            self.Zstage_down.setEnabled(False)
            self.Z1.setEnabled(False)
            self.Z10.setEnabled(False)
            self.Z100.setEnabled(False)
            self.z_distance.setEnabled(False)
            self.z_velocity.setEnabled(False)
            self.z_offset.setEnabled(False)
            # self.Z1.released.connect(lambda: self.Z_instance.set_distance(1))

            # Temperature Buttons
            self.C1_ok.setEnabled(False)
            self.C2_ok.setEnabled(False)
            self.B3_ok.setEnabled(False)
            self.B1_ok.setEnabled(False)
            self.B2_ok.setEnabled(False)
            self.HopL_ok.setEnabled(False)
            self.HopR_ok.setEnabled(False)
            self.B4_ok.setEnabled(False)
            self.B5_ok.setEnabled(False)
            self.B6_ok.setEnabled(False)

            self.browse_files.setEnabled(False)
            self.OK_file_select.setEnabled(False)
            self.get_point.setEnabled(False)
            self.start_print.setEnabled(False)
            self.pause_print.setEnabled(False)
            self.stop_print.setEnabled(False)
        except Exception as e:
            self.parent_connection.send(f"Error M8: Error in start_thread()(button operations)\n{e}")

        # Creating a separate process for automation
        try:
            if self.debug_var == 2:
                self.printToConsole("Creating a new process")
                print("Creating a new process")
            self.stop_event = threading.Event()
            self.auto_process = multiprocessing.Process(target=self.start_process_function)
            self.auto_process.daemon = True
            self.auto_process.start()
        except Exception as e:
            self.parent_connection.send(f"Error M9: Error in start_thread()(Thread operations)\n{e}")

        # Timer (time display)
        try:
            self.time_instant.startTimer()
        except Exception as e:
            self.parent_connection.send(f"Error M10: Error in start_thread()(timer operations)\n{e}")

    def stop_thread(self):  # Fucntion to  handle the stoppage of the automation loop
        self.stop_process.setStyleSheet(self.current_style)
        self.time_instant.resetTimer()
        try:
            #self.auto_process.terminate()
            self.stop_event.set()
        except Exception as e:
            print("No process is running")
            # self.printToConsole("No process is running")
            self.parent_connection.send(f"Error M11: Error in stop_thread()(process terminate)\n{e}")
        try:
            with self.semaphore:  # Acquiring the semaphore
                self.pause_flag.value = False
                self.pause.setText("PAUSE")
        except Exception as e:
            self.parent_connection.send(f"Error M12: Error in stop_thread()(Semaphore)\n{e}")

        # Enabling all the buttons and line edit widgets before starting automation process
        try:
            self.start_process.setEnabled(True)
            self.recoaterRPM.setEnabled(True)
            self.rollerRPM.setEnabled(True)
            self.home.setEnabled(True)
            self.changeDIR.setEnabled(True)
            self.decStop.setEnabled(True)
            self.brake.setEnabled(True)
            self.recoater.setEnabled(True)
            self.set_attributes.setEnabled(True)

            self.RchangeDIR.setEnabled(True)
            self.RdecStop.setEnabled(True)
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

            self.Zaxis_up.setEnabled(True)
            self.Zaxis_down.setEnabled(True)
            self.Zstage_up.setEnabled(True)
            self.Zstage_down.setEnabled(True)
            self.Z1.setEnabled(True)
            self.Z10.setEnabled(True)
            self.Z100.setEnabled(True)
            self.z_distance.setEnabled(True)
            self.z_velocity.setEnabled(True)
            self.z_offset.setEnabled(True)
            # self.Z1.released.connect(lambda: self.Z_instance.set_distance(1))

            # Temperature Buttons
            self.C1_ok.setEnabled(True)
            self.C2_ok.setEnabled(True)
            self.B3_ok.setEnabled(True)
            self.B1_ok.setEnabled(True)
            self.B2_ok.setEnabled(True)
            self.B4_ok.setEnabled(True)
            self.B5_ok.setEnabled(True)
            self.B6_ok.setEnabled(True)
            self.HopL_ok.setEnabled(True)
            self.HopR_ok.setEnabled(True)

            # CLI buttons
            self.browse_files.setEnabled(True)
            self.OK_file_select.setEnabled(True)
            self.get_point.setEnabled(True)
            self.start_print.setEnabled(True)
            self.pause_print.setEnabled(True)
            self.stop_print.setEnabled(True)
        except Exception as e:
            self.parent_connection.send(f"Error M12: Error in stop_thread()(Button operations)\n{e}")

    def start_process_function(self):  # Function to handle the automation loop
        try:
            cmd = "Ready\r"  # Dummy command to the tiva board. Tiva board does not react
            self.serial.serial_write(cmd)
            time.sleep(2)

            hopper_cmdL = {
                "script": "move_hopper_left"
            }

            hopper_cmdR = {
                "script": "move_hopper_right"
            }

            # Setting RPM of Recoater motors
            self.RPM(True, 1, "auto")
            self.waitforResponse()
            self.RPM(False, 1, "auto")
            self.waitforResponse()

            self.waitforPause()

            self.start(False)
            self.waitforResponse()
            self.start(True)
            self.waitforResponse(["L1","L2"])     #Pass arguments to check for specific response like limit switch

            self.start(False)
            self.waitforResponse()
            self.start(True)
            self.waitforResponse(["L1","L2"])

            self.waitforPause()           # To halt the process if pause is clicked


            hopper_cmd = hopper_cmdL
        except Exception as e:
            self.parent_connection.send(f"Error M13: Error in start_process_function()(Pre loop)\n{e}")

        try:
            while not self.stop_event.is_set():  # auotmation loop. order to operation = Z -> Hopper -> Recoater
                try:
                    if self.pause_flag.value == True:
                        # print("PAUSE")
                        self.waitforPause()
                    else:
                        # Move Z axis
                        move_z = {
                            "script": ""
                        }

                        # Open Hopper
                        try:
                            print("Opening Hopper")
                            req = requests.post(url=f"http://{self.api}/printer/gcode/script",
                                                params=hopper_cmd, timeout=2)
                            req.raise_for_status()
                            if hopper_cmd == hopper_cmdL:
                                hopper_cmd = hopper_cmdR
                            elif hopper_cmd == hopper_cmdR:
                                hopper_cmd = hopper_cmdL
                            else:
                                print("Hopper command change error")
                                # if self.debug_var == 2:
                                self.parent_connection.send("Error M14: Hopper command change error")
                                # self.printToConsole("Hopper command change error")
                        except requests.exceptions.Timeout as e:
                            print(f"Error M15: Hopper Request timed out. Connection could not be established.\n{e}")
                            self.parent_connection.send(
                                f"Error M15: Hopper Request timed out. Connection could not be established.\n{e}")
                            # self.mainwindow_console_signal.emit("Hopper Request timed out. Connection could not be established.")
                        except requests.exceptions.RequestException as e:
                            print(f"Error M16: An Hopper request error occurred: {e}")
                            self.parent_connection.send(f"Error M16: An Hopper request error occurred:")
                            # self.mainwindow_console_signal.emit(f"An Hopper request error occurred: {e}")

                        time.sleep(3)

                        # Move Recoater
                        self.changeDirection(False, "auto")
                        self.waitforResponse()
                        self.changeDirection(True, "auto")
                        #self.RwaitforResponse()   No need because it is implemented within the changeDirection Function
                        self.RwaitforResponse()    #Put it back because i removed it from the changeDirection function becuas ethe whole gui was freezing, here it is fine becuase it is a separate thread
                        try:
                            if self.debug_var == 2:
                                print("Moving z")
                                # self.mainwindow_console_signal.emit("Moving in Z direction")
                            req = requests.post(url=f"http://{self.api}/printer/gcode/script",
                                                params=move_z, timeout=2)
                            req.raise_for_status()
                        except requests.exceptions.Timeout as e:
                            print(f"Error M17: Move Z Request timed out. Connection could not be established.")
                            self.parent_connection.send(
                                f"Error M17: Move Z Request timed out. Connection could not be established.\n{e}")
                            # self.mainwindow_console_signal.emit("Hopper Request timed out. Connection could not be established.")
                        except requests.exceptions.RequestException as e:
                            print(f"Error M18: A Z request error occurred: {e}")
                            self.parent_connection.send(f"Error M18: A Z request error occurred: {e}")
                            # self.mainwindow_console_signal.emit(f"An Hopper request error occurred: {e}")
                        time.sleep(3)  # Need to configure waitforResponse for octopus communication also

                except Exception as e:
                    print(f"Loop error\n {e}")
                    self.parent_connection.send(f"Loop error\n {e}")
                    continue

            self.stop_event.clear()                     # To make sure the next call of this functions executes properlly and gets into the while loop
        except Exception as e:
            print("Auto process error \n {e}")
            # self.printToConsole("Auto process error")

    def environment_control(self):  # Function to handle the environment management process
        try:
            while True:
                self.lock.acquire()
                self.temperature = self.environment_instance.update_screen()
                self.lock.release()
                time.sleep(5)
        except Exception as e:
            self.parent_connection.send(f"Error M19: Error in environment_control(): {e}")

    def update_gui_temp(self, status):
        # Current Temperature
        try:
            if "tiva" in status.keys():
                if status["tiva"] == "Online":
                    self.tiva_status.setText("Tiva Online")
                    self.tiva_status.setStyleSheet("color: green")
                else:
                    self.tiva_status.setText("Tiva Offline")
                    self.tiva_status.setStyleSheet("color: red")

            if "Octopus" in status.keys():
                if status["Octopus"] == "Online":
                    self.MCU_Status.setText("Octopus Online")
                    self.MCU_Status.setStyleSheet("color: green")
                else:
                    self.MCU_Status.setText("Octopus Offline")
                    self.MCU_Status.setStyleSheet("color: red")

            if "Temperature_data" in status.keys():
                temperatures = status["Temperature_data"]
                print(temperatures,status.keys())

                if temperatures != "":
                    try:
                        self.C1_Temp.setText(str(temperatures["chamber"]["actual"]))
                        self.C2_Temp.setText(str(temperatures["chamber"]["actual"]))
                        self.B1_Temp.setText(str(temperatures["bed"]["actual"]))
                        self.B2_Temp.setText(str(temperatures["bed"]["actual"]))
                        self.B3_Temp.setText(str(temperatures["bed"]["actual"]))
                        self.B4_Temp.setText(str(temperatures["bed"]["actual"]))
                        self.B5_Temp.setText(str(temperatures["bed"]["actual"]))
                        self.B6_Temp.setText(str(temperatures["bed"]["actual"]))
                        self.HopL_Temp.setText(str(temperatures["tool0"]["actual"]))
                        self.HopR_Temp.setText(str(temperatures["tool1"]["actual"]))
                    except Exception as e:
                        self.parent_connection.send(f"Error M66: Error in update_gui_temp()(Temeprature assignment)\n{e}")


                    # Heater state
                    try:
                        if temperatures["chamber"]["actual"] < temperatures["chamber"]["target"]:
                            self.C1_state.setText("ON")
                        else:
                            self.C1_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M54: Error in update_gui_temp()(checking chamber 1 temperature)\n{e}")

                    try:
                        if temperatures["chamber1"]["actual"] < temperatures["chamber1"]["target"]:     #Change values with appropriate ones
                            self.C2_state.setText("ON")
                        else:
                            self.C2_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M55: Error in update_gui_temp()(checking chamber 2 temperature)\n{e}")

                    try:
                        if temperatures["bed1"]["actual"] < temperatures["bed1"]["target"]:
                            self.B1_state.setText("ON")
                        else:
                            self.B1_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M56: Error in update_gui_temp()(checking Bed 1 temperature)\n{e}")

                    try:
                        if temperatures["bed2"]["actual"] < temperatures["bed2"]["target"]:
                            self.B2_state.setText("ON")
                        else:
                            self.B2_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M57: Error in update_gui_temp()(checking Bed 2 temperature)\n{e}")

                    try:
                        if temperatures["bed3"]["actual"] < temperatures["bed3"]["target"]:
                            self.B3_state.setText("ON")
                        else:
                            self.B3_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M58: Error in update_gui_temp()(checking Bed 3 temperature)\n{e}")

                    try:
                        if temperatures["bed4"]["actual"] < temperatures["bed4"]["target"]:
                            self.B4_state.setText("ON")
                        else:
                            self.B4_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M59: Error in update_gui_temp()(checking Bed 4 temperature)\n{e}")

                    try:
                        if temperatures["bed5"]["actual"] < temperatures["bed5"]["target"]:
                            self.B5_state.setText("ON")
                        else:
                            self.B5_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M60: Error in update_gui_temp()(checking Bed 5 temperature)\n{e}")

                    try:
                        if temperatures["bed6"]["actual"] < temperatures["bed6"]["target"]:
                            self.B6_state.setText("ON")
                        else:
                            self.B6_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M61: Error in update_gui_temp()(checking Bed 6 temperature)\n{e}")

                    try:
                        if temperatures["tool0"]["actual"] < temperatures["tool0"]["target"]:
                            self.HopL_state.setText("ON")
                        else:
                            self.HopL_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M62: Error in update_gui_temp()(checking Left Hopper temperature)\n{e}")

                    try:
                        if temperatures["tool1"]["actual"] < temperatures["tool1"]["target"]:
                            self.HopR_state.setText("ON")
                        else:
                            self.HopR_state.setText("OFF")
                    except Exception as e:
                        self.parent_connection.send(f"Error M63: Error in update_gui_temp()(checking Right Hopper temperature)\n{e}")

        except Exception as e:
            print(f"GUI updation failed with error \n{e}")
            self.parent_connection.send(f"Error M20: Error in update_gui_temp(): {str(e)}")

    def R_motion_attributes(self):
        try:
            self.set_attributes.setStyleSheet(self.current_style)
            global PITCH, GEAR_RATIO, FAST_RPM_DISTANCE, SLOW_RPM_DISTANCE, FAST_RPM, SLOW_RPM
            try:
                pitch = int(self.pitch.text())
            except ValueError:
                print("Invalid pitch input, taking default value")
                pitch = PITCH
                self.parent_connection.send(f"Error M21: Invalid pitch input, taking default value")
            try:
                f_rpm_d = int(self.fast_rpm_distance.text())
            except ValueError:
                print("Invalid fast RPM distance input, taking default value")
                f_rpm_d = FAST_RPM_DISTANCE
                self.parent_connection.send(f"Error M22: Invalid fast RPM distance input,considering default value")

            try:
                s_rpm_d = int(self.slow_rpm_distance.text())
            except ValueError:
                print("Invalid slow RPM distance input, taking default value")
                s_rpm_d = SLOW_RPM_DISTANCE
                # self.printToConsole("Invalid slow RPM distance input, taking default value")
                self.parent_connection.send(f"Error M23: Invalid slow RPM distance input, taking default value")

            try:
                gear_ratio = int(self.gear_ratio.text())
            except ValueError:
                print("Invalid gear ratio input, taking default value")
                gear_ratio = GEAR_RATIO
                # self.printToConsole("Invalid gear ratio input, taking default value")
                self.parent_connection.send(f"Error M24: Invalid gear ratio input, taking default value")

            try:
                fast_rpm = int(self.fast_rpm.text())
            except ValueError:
                print("Invalid fast RPM input, taking default value")
                fast_rpm = FAST_RPM
                # self.printToConsole("Invalid fast RPM input, taking default value")
                self.parent_connection.send(f"Error M25: Invalid fast RPM input, taking default value")

            try:
                slow_rpm = int(self.slow_rpm.text())
            except ValueError:
                print("Invalid slow RPM input, taking default value")
                slow_rpm = SLOW_RPM
                # self.printToConsole("Invalid slow RPM input, taking default value")
                self.parent_connection.send(f"Error M26: Invalid slow RPM input, taking default value")

            if self.debug_var == 2:
                self.parent_connection.send(
                    f"New attributes \n pitch:{pitch};Fast RPM Distance:{f_rpm_d};Slow RPM Distance:{s_rpm_d};Gear Ratio:{gear_ratio};Fast RPM:{fast_rpm}; Slow RPM: {slow_rpm}")
                print(
                    f"New attributes \n pitch:{pitch};Fast_D :{f_rpm_d};Slow_D:{s_rpm_d};Gear Ratio:{gear_ratio};Fast RPM:{fast_rpm}; Slow RPM: {slow_rpm}")

                # 2         #7            #16           #14            #18           #22
            attr = f"P {pitch} FD {f_rpm_d} SD {s_rpm_d} GR {gear_ratio} FR {fast_rpm} SR {slow_rpm} \r"
            # print(attr[2],attr[7],attr[12],attr[17],attr[22],attr[27])
            # for i in attr:
            #     print(i)
            self.serial.serial_write(attr)
        except Exception as e:
            print(f"R motion attribute setting failed with error:\n {e}")
            # self.printToConsole(f"R motion attribute setting failed with error:\n {e}")
            self.parent_connection.send(f"Error M27: R motion attribute setting failed with error:\n {e}")

    def R_disable_buttons(self):
        try:
            self.start_process.setEnabled(False)
            self.recoaterRPM.setEnabled(False)
            self.rollerRPM.setEnabled(False)
            self.home.setEnabled(False)
            self.changeDIR.setEnabled(False)
            self.decStop.setEnabled(False)
            self.brake.setEnabled(False)
            self.recoater.setEnabled(False)
            self.set_attributes.setEnabled(False)
            self.RchangeDIR.setEnabled(False)
            self.RdecStop.setEnabled(False)
            self.Rbrake.setEnabled(False)
            self.roller.setEnabled(False)
        except Exception as e:
            self.parent_connection.send(f"Error M27: Error in R_disable_buttons\n {e}")

    def R_enable_buttons(self):
        try:
            self.start_process.setEnabled(True)
            self.recoaterRPM.setEnabled(True)
            self.rollerRPM.setEnabled(True)
            self.home.setEnabled(True)
            self.changeDIR.setEnabled(True)
            self.decStop.setEnabled(True)
            self.brake.setEnabled(True)
            self.recoater.setEnabled(True)
            self.set_attributes.setEnabled(True)
            self.RchangeDIR.setEnabled(True)
            self.RdecStop.setEnabled(True)
            self.Rbrake.setEnabled(True)
            self.roller.setEnabled(True)
        except Exception as e:
            self.parent_connection.send(f"Error M28: Error in R_enable_buttons\n {e}")

    def Home_recoater(self):  # Function to home the recoater system
        try:
            self.home.setStyleSheet(self.current_style)
        except Exception as e:
            self.parent_connection.send(f"Error M29: Error in Home_recoater(stylesheet)\n {e}")
        if self.debug_var == 2:
            self.parent_connection.send("Homing recoater system")
        try:
            cmd = "Recoater_RUN_FW\r"
            if self.debug_var == 2:
                #self.parent_connection.send(f"Command:{cmd}")
                print(f"Command:{cmd}")
            self.serial.serial_write(cmd)
            self.homming = True
            #self.R_disable_buttons()             # I dont think we need to disable the buttons because enabling them will become tedious
        except Exception as e:
            #self.R_enable_buttons()
            self.homming = False
            print("Homing error \n {e}")
            self.parent_connection.send(f"Error M30: Error in Home_recoater\n {e}")

    def recoater_emergency(self):  # Function to handing the emergency stoppage of the recoater system
        try:
            print("Emergency recoater stop initiated")
            self.parent_connection.send("Emergency recoater stop initiated")
            self.recoater_Estop.setStyleSheet(self.current_style)
        except Exception as e:
            self.parent_connection.send(f"Error M31: Error in recoater_emergency(stylesheet)\n{e}")
        try:
            cmd = "Recoater_STOP_IN\r"
            self.serial.serial_write(cmd)

            time.sleep(1)

            cmd = "Roller_STOP_IN\r"
            self.serial.serial_write(cmd)
        except Exception as e:
            print("Recoater emergerncy stop errror \n {e}")
            self.parent_connection.send(f"Error M32: Error in recoater_emergency\n {e}")

    # def printToConsole(self, text):  # Function to print the console in the UI
    #     #print("Hi Console")
    #     # Add text to the console
    #     try:
    #         if isinstance(text,str):
    #             self.console.append("AMCOE/system/console$" + text)
    #             return
    #         data = ""
    #         error = ""
    #         if "data" in text.keys():
    #             data = text["data"]
    #         if "error" in text.keys():
    #             error = text["error"]
    #         if data != "":
    #             self.console.append("AMCOE/system/console$" + data)
    #         if error != "":
    #             self.console.append("AMCOE/system/console$" + error)
    #     except Exception as e:
    #         self.parent_connection.send(f"Error M33: Error in printToConsole\n {e}")

    def printToConsole(self, text):  # Trying colors
        # print("Hi Console")
        # Add text to the console
        try:
            cursor = self.console.textCursor()
            cursor.movePosition(cursor.End)
            if isinstance(text, str):  # Almost never called, becuase i am routing all signals to read thread  (Directly calling the printoconsole function is very rare)
                text = text + "\n"
                if "Error" in text:
                    cursor.setCharFormat(RED)
                    cursor.insertText(text)
                else:
                    cursor.setCharFormat(GREEN)
                    cursor.insertText(text)
                # self.console.append("AMCOE/system/console$" + text)
                return
            data = ""
            error = ""
            if "data" in text.keys():
                data = text["data"]
                data = "AMCOE/system/console$" + data + "\n"
            if "error" in text.keys():
                error = text["error"]
                error = "AMCOE/system/console$" + error + "\n"
            if data != "":
                # self.console.append("AMCOE/system/console$" + data)
                cursor.setCharFormat(GREEN)
                cursor.insertText(data)
            if error != "":
                cursor.setCharFormat(RED)
                cursor.insertText(error)
                # self.console.append("AMCOE/system/console$" + error)
        except Exception as e:
            self.parent_connection.send(f"Error M33: Error in printToConsole\n {e}")

    def printToSerialMonitor(self, text):  # Function to print the console in the UI
        # print("Hi Serial Console")
        # Add text to the console
        try:
            if "data" in text.keys():
                data = text["data"]
                # print("Printing inside the if statement")
                self.serial_monitor.append("AMCOE/system/console$" + data)
                if "Ex17" in data or "Ex18" in data:
                    self.R_enable_buttons()
            if "L1" in text.keys() or "L2" in text.keys():
                if self.homming == True:
                    try:
                        print("going back")
                        cmd = "Recoater_RUN_RV\r"
                        if self.debug_var == 2:
                            #elf.parent_connection.send(f"Command:{cmd}")
                            print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                        self.homming = False
                        #self.R_disable_buttons()             # I dont think we need to disable the buttons because enabling them will become tedious
                    except Exception as e:
                        #self.R_enable_buttons()
                        self.homming = False
                        print("Homing error \n {e}")
                        self.parent_connection.send(f"Error M30: Error in Home_recoater\n {e}")
                    global MOTOR_DIR
                    MOTOR_DIR = False

                self.R_enable_buttons()
                # if "L1" in text.keys():
                #     self.limitSwitchRight.setText(text["clicked"])
                #     self.limitSwitchLeft.setText(text["open"])
                # elif "L2" in text.keys():
                #     self.limitSwitchRight.setText(text["open"])
                #     self.limitSwitchLeft.setText(text["clicked"])
                # else:
                #     self.limitSwitchRight.setText(text["open"])
                #     self.limitSwitchLeft.setText(text["open"])

        except Exception as e:
            self.parent_connection.send(f"Error M34: Error in printToSerialMonitor\n {str(e)}")

    def RPM(self, rpm, num, auto="0"):  # Function to set the RPM to the motors in the recoater system
        try:
            global RECOATER_RPM
            global ROLLER_RPM
            if rpm == True and num == 0:  # When RPM is set using line edit widget, i.e entering the value for MOTOR 1
                val = self.recoaterRPM.text()
                if val.isdigit():
                    val = int(val)
                    RECOATER_RPM = val
                    print(f"new recoater rpm: {RECOATER_RPM}")
                    if auto != "auto":
                        self.parent_connection.send(f"new recoater rpm: {RECOATER_RPM}")
                    if val < 40 or val > 3150:
                        print("Please enter valid inputs")
                        if auto != "auto":
                            self.parent_connection.send("Please enter valid inputs")
                    else:
                        if self.serial.serial.is_open:
                            cmd = "Recoater_RPM" + f" {RECOATER_RPM}\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                        else:
                            print("Serial port is not open")
                            if auto != "auto":
                                self.parent_connection.send("Serial port is not open")

                else:
                    print("Please enter valid inputs")
                    if auto != "auto":
                        self.parent_connection.send("Please enter valid inputs")
            elif rpm == False and num == 0:  # Setting rpm for motor 2 by direct entry
                val = self.rollerRPM.text()
                if val.isdigit():
                    val = int(val)
                    ROLLER_RPM = val
                    print(f"new roller rpm: {ROLLER_RPM}")
                    if val < 0 or val > 3150:
                        print("Please enter valid inputs")
                        if auto != "auto":
                            self.parent_connection.send("Please enter valid inputs")
                    else:
                        if self.serial.serial.is_open:
                            cmd = "Roller_RPM" + f" {ROLLER_RPM}\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                        else:
                            print("Serial port is not open")
                            if auto != "auto":
                                self.parent_connection.send("Serial port is not open")

                else:
                    print("Please enter valid inputs")
                    if auto != "auto":
                        self.parent_connection.send("Please enter valid inputs")
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
                    cmd = "Recoater_RPM" + f" {RECOATER_RPM}\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        if auto != "auto":
                            self.parent_connection.send(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    self.parent_connection.send("Serial port is not open")

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
                    cmd = "Roller_RPM" + f" {ROLLER_RPM}\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        if auto != "auto":
                            self.parent_connection.send(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    if auto != "auto":
                        self.parent_connection.send("Serial port is not open")
        except Exception as e:
            print(f"RPM error \n {e}")
            if auto != "auto":
                self.parent_connection.send(f"Error M35: Error in RPM\n {e}")
            if self.debug_var == 2:
                print("Trying to open new serial port")
                if auto != "auto":
                    self.parent_connection.send("Trying to open new serial port")
                try:
                    self.serial.connect()
                except:
                    print("unable to establish serial communication")
                    self.parent_connection.send(f"Error M35: Error in RPM(serial retry)\n {e}")
                    if auto != "auto":
                        self.parent_connection.send("Trying to open new serial port")

    def start(self, motor_select):  # Function to handle the start of the motors
        try:
            global MOTOR_DIR
            if motor_select:  # Motor 1
                self.recoater.setStyleSheet(
                    self.current_style)  # this type of line in all functions is used for the click effect
                if self.serial.serial.is_open:
                    if MOTOR_DIR:
                        cmd = "Recoater_RUN_RV\r"  # Recoater_RUN_FW    #Normal recoater motion speed
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.parent_connection.send(f"Command:{cmd}")
                            self.parent_connection.send(f"Linear right motion")
                        self.serial.serial_write(cmd)
                        # self.recoater_normal_motion_direction = False
                        MOTOR_DIR = False
                        self.changeDIR.setText("Move right")
                    else:
                        cmd = "Recoater_RUN_FW\r"  # Recoater_RUN_RV   #Recoater_START\r
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.parent_connection.send(f"Command:{cmd}")
                            self.parent_connection.send(f"Linear left motion")
                        self.serial.serial_write(cmd)
                        # self.recoater_normal_motion_direction = True
                        MOTOR_DIR = True
                        self.changeDIR.setText("Move left")
                else:
                    print("Serial port is not open")
                    self.parent_connection.send("Error M36: Serial port is not open")

            else:  # Motor 2
                self.roller.setStyleSheet(self.current_style)
                if self.serial.serial.is_open:
                    cmd = "Roller_START\r"  # Roller_START\r
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        self.parent_connection.send(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    self.parent_connection.send("Error M37: Serial port is not open")

        except Exception as e:
            print(f"start function Error\n {e}")
            self.parent_connection.send("Error M38: Error in start()")
            print("Trying to open new serial port")
            self.parent_connection.send("Trying to open new serial port")
            try:
                self.serial.open()
            except Exception as e:
                print(f"unable to establish serial communication due to \n {e}")
                self.parent_connection.send(f"Error M39: unable to establish serial communication due to \n {e}")

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
                        cmd = "Recoater_BRAKE\r"  # Recoater_BRAKE\r
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.parent_connection.send(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print("Error in braking Motor 1")
                        self.parent_connection.send(f"Error M40: Error in Brake()(Motor 1)\n {e}")
                else:
                    self.Rbrake.setStyleSheet(self.current_style)  # R prefix indicated motor 2 / ROLLER
                    try:
                        cmd = "Roller_BRAKE\r"  # Roller_BRAKE\r
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print("Error in braking R Motor")
                        self.parent_connection.send(f"Error M40: Error in Brake()(Motor 2)\n {e}")

            else:
                print("Unable to detect a serial connection")
                # self.printToConsole("Unable to detect a serial connection")
                self.parent_connection.send(f"Error M41: Error in Brake()(serial)\n")

        except Exception as e:
            print("Error in brake function \n {e}")
            # self.printToConsole("Error in brake function")
            self.parent_connection.send(f"Error M42: Error in Brake()\n {e}")

    def instantStop(self,
                    motor_select):  # Function to instantaneously stop the motor, the buttons are not displayed in the GUI
        try:
            if self.serial.serial.is_open:
                if motor_select:
                    try:
                        cmd = "Recoater_STOP_IN\r"
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.parent_connection.send(f"COMMAND:{cmd}")
                        self.serial.serial_write(cmd)

                    except Exception as e:
                        print(f"Error in INSTANTANEOUSLY braking Motor 1 \n {e}")
                        self.parent_connection.send(f"Error M43: Error in instantStop()(Motor 1)\n {e}")
                else:
                    try:
                        cmd = "Roller_STOP_IN\r"
                        print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in INSTANTANEOUSLY braking R Motor\n{e}")
                        self.parent_connection.send(f"Error M44: Error in instantStop()(Motor 2)\n {e}")

            else:
                print("Unable to detect a serial connection")
                # self.printToConsole("Unable to detect a serial connection")
                self.parent_connection.send(f"Error M44: Error in instantStop()(Serial)\n")

        except:
            print("Error in instant brake function")
            # self.printToConsole("Error in instant brake function")
            self.parent_connection.send(f"Error M45: Error in instantStop()\n {e}")

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
                        cmd = "Recoater_STOP_DC\r"
                        if self.debug_var == 2:
                            self.parent_connection.send(f"Command:{cmd}")
                            print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in DECELERATING brakes in Motor 1\n{e}")
                        # self.printToConsole("Error in DECELERATING brakes in Motor 1")
                        self.parent_connection.send(f"Error M46: Error in deceleratingStop()(Motor 1)\n {e}")
                else:
                    self.RdecStop.setStyleSheet(self.current_style)
                    try:
                        cmd = "Roller_STOP_DC\r"
                        if self.debug_var == 2:
                            self.parent_connection.send(f"Command:{cmd}")
                            print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in DECELERATING brakes in R Motor\n{e}")
                        self.parent_connection.send(f"Error M47: Error in deceleratingStop()(Motor 2)\n {e}")

            else:
                print("Unable to detect a serial connection")
                self.parent_connection.send(f"Error M48: Error in deceleratingStop()(Serial)\n")

        except Exception as e:
            print(f"Error in decelerating brake function\n{e}")
            self.parent_connection.send(f"Error M49: Error in deceleratingStop()\n {e}")

    def changeDirection(self, motor_select,
                        auto="0"):  # Function to handle the change of direction of motion of recoater motors
        try:
            if auto == "0":
                if motor_select:
                    self.changeDIR.setStyleSheet(self.current_style)
                else:
                    self.RchangeDIR.setStyleSheet(self.current_style)
        except Exception as e:
            self.parent_connection.send(f"Error M50: Error in changeDirection()(Stylesheet)\n {e}")

        try:
            global MOTOR_DIR
            global RMOTOR_DIR
            if self.serial.serial.is_open:
                if motor_select:
                    self.changeDIR.setStyleSheet(self.current_style)
                    try:
                        self.R_disable_buttons()
                        if MOTOR_DIR:  # Variable to store the direction of motion
                            cmd = "Recoater_Go_Right\r"  # Recoater_Go_Left\r
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            MOTOR_DIR = False
                            if auto != "auto":
                                self.changeDIR.setText("Move Right")
                        else:
                            cmd = "Recoater_Go_Left\r"  # Recoater_Go_Right\r
                            self.serial.serial_write(cmd)
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            MOTOR_DIR = True
                            if auto != "auto":
                                self.changeDIR.setText("Move left")
                        #self.RwaitforResponse()                                     #The complete GUI will wait for this therefore not using it here
                            if auto == "auto":
                                self.RwaitforResponse()                             #In the synchronous process the sub thread will wait but the main thread will continue to run
                    except Exception as e:
                        self.R_enable_buttons()
                        print(f"Error in changing direction of roation of Motor 1\n{e}")
                        # if auto != "auto":
                        #     self.printToConsole("Error in changing direction of roation of Motor 1")
                        if auto != "auto":
                            # self.printToConsole(f"Error in changing direction of roation of Motor 1\n{e}")
                            self.parent_connection.send(f"Error M51: Error in changeDirection()(Motor 1)\n {e}")

                else:
                    if auto == "0":
                        self.RchangeDIR.setStyleSheet(self.current_style)
                    try:
                        if RMOTOR_DIR:
                            cmd = "Roller_RUN_RV\r"  # Roller_RUN_RV\r
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                                print(f"Command:{cmd}")

                            print(f"command:{cmd}")
                            self.serial.serial_write(cmd)
                            RMOTOR_DIR = False
                            if auto != "auto":
                                self.RchangeDIR.setText("AntiClockwise")
                        else:
                            cmd = "Roller_RUN_FW\r"  # Roller_RUN_FW\r
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            RMOTOR_DIR = True
                            if auto != "auto":
                                self.RchangeDIR.setText("Clockwise")
                    except Exception as e:
                        print(f"Error in changing direction of roation of Motor 2\n{e}")
                        if auto != "auto":

                            # self.printToConsole("Error in changing direction of rotation of Motor 2")
                            self.parent_connection.send(f"Error M52: Error in changeDirection()(Motor 2)\n {e}")
            else:
                print("Serial port not open")
                if auto != "auto":
                    self.parent_connection.send(f"Error M52: Error in changeDirection()(Serial)\n {e}")

        except Exception as e:
            print("Error in the direction changing function\n{e}")
            if auto != "auto":
                # self.printToConsole("Error in the direction changing function")
                self.parent_connection.send(f"Error M52: Error in changeDirection()\n {e}")

    def dynamic_commands(self):
        command = self.Command_input.text()
        if command in R_Commands:
            self.parent_connection.send(f"{command}")
            command = command + "\r"
            self.serial.serial_write(command)
        elif command in H_Commands:
            try:
                req = requests.post(url=f"http://{self.api}/printer/gcode/script", params=command,
                                    timeout=2)
                req.raise_for_status()
                if req.raise_for_status() == 200:
                    if self.debug_var == 2:
                        print("Dynamic hopper command successful")
                        self.parent_connection.send("Dynamic hopper command successful")

                else:
                    if self.debug_var == 2:
                        print("Dynamic hopper command failed")
                        #self.console_signal.emit("Right hopper command failed")
                        self.parent_connection.send(f"Dynamic hopper command failed")

            except requests.exceptions.Timeout as e:
                #print("Dynamic Hopper Request timed out. Connection could not be established.")
                self.parent_connection.send(f"Error DH1: Dynamic Hopper command Timeout \n{e}")
            except requests.exceptions.RequestException as e:
                #print(f"An Hopper request error occurred: {e}")
                #self.console_signal.emit(f"An Hopper request error occurred: {e}")
                self.parent_connection.send(f"Error DH2: Dynamic Hopper command request error\n{e}")
            except Exception as e:
                #print("Error in Dose function \n {e}")
                #self.mainHopperInstance.parent_connection.send("Error in Dose function")
                self.parent_connection.send(f"Error DH3: Dynamic Hopper command error\n{e}")

        elif command in Z_Commands:
            try:
                try:
                    print("Moving z")
                    req = requests.post(url=f"http://{self.api}/printer/gcode/script", params=command, timeout=5)
                    req.raise_for_status()
                except requests.exceptions.Timeout:
                    #print("Move Z Request timed out. Connection could not be established.")
                    #self.console_sig.emit("Move Z Request timed out. Connection could not be established.")
                    self.parent_connection.send(f"Error DZ1: Dynamic Z command timeout")
                except requests.exceptions.RequestException as e:
                    #print(f"A Z request error occurred: {e}")
                    #self.console_sig.emit(f"A Z request error occurred: {e}")
                    self.parent_connection.send(f"Error DZ2: Dynamic Z command request error")
                #time.sleep(1)
            except Exception as e:
                print(f"Error in Z function \n {e}")
                #self.console_sig.emit(f"Error in Z function \n {e}")
                self.parent_connection.send(f"Error DZ3: Dynamic Z command error")
                # self.printToConsole("Error in Dose function")

        elif command == "clear":
            self.console.clear()

        elif command == "smclear":
            self.serial_monitor.clear()

        else:
            self.parent_connection.send(f"Invalid Command: '{command}'")



def main():
    app = QApplication([])
    parent_conn, child_conn = multiprocessing.Pipe()
    scanner_parent_conn, scanner_child_conn = multiprocessing.Pipe()
    window = GUI(parent_conn, child_conn, scanner_parent_conn, scanner_child_conn)
    app.exec_()


if __name__ == '__main__':
    main()
