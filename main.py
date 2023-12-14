from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QObject, pyqtSignal
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

RECOATER_RPM = 100
ROLLER_RPM = 100
MOTOR_DIR = False
RMOTOR_DIR = False


class GUI(QMainWindow, QObject):
    mainwindow_console_signal = pyqtSignal(str)

    def __init__(self, parent_conn, child_conn):
        try:
            super(GUI, self).__init__()
            self.MainWindow = uic.loadUi("27Oct(Ganesh).ui", self)
            self.environment_instance = Environment(self)
            self.hopper = Hopper(self)  # Hopper class instance
            self.Z_instance = Zmotion(self)  # Z class instance
            self.serial = Serial_Class(self)
            self.time_instant = Time(self)
            # self.auto_process = Automation(self)
            self.cli_file_object = None
            self.file_path = ""

            self.debug_var = 1

            self.parent_connection = parent_conn

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
            self.api = "127.0.0.1"
            self.params = {"apikey": 'B508534ED20348F090B4D0AD637D3660'}

            self.lock = threading.Lock()  # Lock variable, for synchronisation purpose
            self.acknowledgement = True
            self.semaphore = multiprocessing.Semaphore(1)
            self.pause_flag = multiprocessing.Value('b', False)  # Creating a shared variable

            # Calling connect function
            self.serial.connect()

            # Start a separate thread for reading and displaying serial data
            self.read_thread = threading.Thread(target=self.serial.readData, args=(child_conn,))
            self.read_thread.daemon = True
            self.read_thread.start()

            # Start a separate thread for refreshing the temperature screen
            self.environment_thread = threading.Thread(target=self.environment_control)
            self.environment_thread.daemon = True
            self.environment_thread.start()

            # UI widgets initialisation
            self.start_process.released.connect(self.start_thread)  # Use lambda when you have to pass arguments
            self.stop_process.released.connect(self.stop_thread)
            self.pause.released.connect(self.pause_auto_process)

            #CLI file widgets
            self.browse_files.released.connect(self.open_file_dialog)
            self.OK_file_select.released.connect(self.cli_final_select)
            self.get_point.released.connect(self.get_next_coordinates)


            # Debug level selector
            self.DebugLevel.activated.connect(self.Select_debug_level)

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

            self.Zaxis_up.pressed.connect(lambda: self.ButtonClickEffect(self.Zaxis_up))
            self.Zaxis_down.pressed.connect(lambda: self.ButtonClickEffect(self.Zaxis_down))
            self.Zstage_up.pressed.connect(lambda: self.ButtonClickEffect(self.Zstage_up))
            self.Zstage_down.pressed.connect(lambda: self.ButtonClickEffect(self.Zstage_down))
            self.Z1.pressed.connect(lambda: self.ButtonClickEffect(self.Z1))
            self.Z10.pressed.connect(lambda: self.ButtonClickEffect(self.Z10))
            self.Z100.pressed.connect(lambda: self.ButtonClickEffect(self.Z100))

            # Temperature Buttons
            self.C1_ok.pressed.connect(lambda: self.ButtonClickEffect(self.C1_ok))
            self.C2_ok.pressed.connect(lambda: self.ButtonClickEffect(self.C2_ok))
            self.C3_ok.pressed.connect(lambda: self.ButtonClickEffect(self.C3_ok))
            self.B1_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B1_ok))
            self.B2_ok.pressed.connect(lambda: self.ButtonClickEffect(self.B2_ok))
            self.HopL_ok.pressed.connect(lambda: self.ButtonClickEffect(self.HopL_ok))
            self.HopR_ok.pressed.connect(lambda: self.ButtonClickEffect(self.HopR_ok))

            #Hopper Dose Button
            self.Hopper_Dose.pressed.connect(lambda: self.ButtonClickEffect(self.Hopper_Dose))

            #CLI file buttons
            self.browse_files.pressed.connect(lambda: self.ButtonClickEffect(self.browse_files))
            self.OK_file_select.pressed.connect(lambda: self.ButtonClickEffect(self.OK_file_select))
            self.get_point.pressed.connect(lambda: self.ButtonClickEffect(self.get_point))


            self.show()

        except Exception as e:
            print(f"Program initialisation failed with error: {e}")
            self.parent_connection.send("Program initialisation failed")

    def open_file_dialog(self):
        self.browse_files.setStyleSheet(self.current_style)
        try:
            options = QFileDialog.Options()
            file_dialog = QFileDialog()
            self.file_path, _ = file_dialog.getOpenFileName(self, "Select File", "", "All Files (*);;Text Files (*.txt)", options=options)

            if self.file_path:
                self.file_entry.setText(self.file_path)
        except Exception as e:
            print(e)

    def cli_final_select(self):
        self.OK_file_select.setStyleSheet(self.current_style)
        try:
            self.file_path = self.file_entry.text()
            if self.file_path:
                self.cli_file_object = Marking_Data(self, self.file_path)
                print(self.file_path)

            if not self.cli_file_object.checkForErrors():
                self.cli_file_object.generate_data()
        except Exception as e:
            print(e)

    def get_next_coordinates(self):
        self.get_point.setStyleSheet(self.current_style)
        try:
            if self.cli_file_object is not None:
                point = self.cli_file_object.get_next_pair()
                point = "(" + str(point[0]) + "," + str(point[1]) + ")" +","+ f"unit: {self.cli_file_object.unit}"
                print(point)
                self.point_display.setText(point)
        except Exception as e:
            print(e)


    def page_change(self, page):
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

    def Select_debug_level(self):
        self.debug_var = int(self.DebugLevel.currentText())
        print("Debug level changed to ", self.debug_var)
        self.parent_connection.send(f"Debug level changed to {self.debug_var}")

    def ButtonClickEffect(self, object):
        self.current_style = object.styleSheet()  # Obtaining current style sheet
        new_style = ""
        current_style = self.current_style
        for line in current_style.split(';'):  # Checking for background-color line
            if line.strip().startswith("background"):
                line = line.split(":")
                line[1] = line[1].strip()
                rgb = line[1][4:len(line[1]) - 1].split(",")
                red = int(rgb[0])
                green = int(rgb[1])
                blue = int(rgb[2])
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
                new_style = new_style + line + ";"
        new_color = f"\nbackground-color: rgb({new_red}, {new_green}, {new_blue});"
        new_style = current_style + new_color
        object.setStyleSheet(new_style)  # applying the new stylesheet

    def pause_auto_process(self):  # Function to pause the automation loop
        self.pause.setStyleSheet(self.current_style)
        with self.semaphore:  # Acquiring the semaphore
            if self.pause_flag.value == True:
                self.pause_flag.value = False
                self.pause.setText("PAUSE")
                self.time_instant.resumeTimer()
                self.printToConsole("process resumed")
            else:
                self.pause_flag.value = True
                self.pause.setText("RESUME")
                self.time_instant.stopTimer()
                self.printToConsole("process paused")

    def start_thread(self):  # Function to initialise and start the automation loop
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
        self.C3_ok.setEnabled(False)
        self.B1_ok.setEnabled(False)
        self.B2_ok.setEnabled(False)
        self.HopL_ok.setEnabled(False)
        self.HopR_ok.setEnabled(False)

        # Creating a separate process for automation
        if self.debug_var == 2:
            self.printToConsole("Creating a new process")
            print("Creating a new process")
        self.auto_process = multiprocessing.Process(target=self.start_process_function)
        self.auto_process.daemon = True
        self.auto_process.start()

        # Timer
        self.time_instant.startTimer()

    def stop_thread(self):  # Fucntion to  handle the stoppage of the automation loop
        self.stop_process.setStyleSheet(self.current_style)
        self.time_instant.resetTimer()
        try:
            self.auto_process.terminate()
        except:
            print("No process is running")
            self.printToConsole("No process is running")

        with self.semaphore:  # Acquiring the semaphore
            self.pause_flag.value = False
            self.pause.setText("PAUSE")

        # Enabling all the buttons and line edit widgets before starting automation process
        self.start_process.setEnabled(True)
        self.recoaterRPM.setEnabled(True)
        self.rollerRPM.setEnabled(True)
        self.home.setEnabled(True)
        self.changeDIR.setEnabled(True)
        self.decStop.setEnabled(True)
        self.brake.setEnabled(True)
        self.recoater.setEnabled(True)

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
        self.C3_ok.setEnabled(True)
        self.B1_ok.setEnabled(True)
        self.B2_ok.setEnabled(True)
        self.HopL_ok.setEnabled(True)
        self.HopR_ok.setEnabled(True)

    def start_process_function(self):  # Function to handle the automation loop
        import time as ti
        try:
            cmd = "Ready\r"  # Dummy command to the tiva board. Tiva board does not react
            self.serial.serial_write(cmd)
            ti.sleep(2)

            hopper_cmdL = {
                "script": "move_hopper_left"
            }

            hopper_cmdR = {
                "script": "move_hopper_right"
            }

            # Setting RPM of Recoater motors
            self.RPM(True, 1, "auto")
            ti.sleep(2)
            self.RPM(False, 1, "auto")
            ti.sleep(2)
            # self.printToConsole("RPM setting finished")

            # Homming Recoater System
            self.changeDirection(False, "auto")
            ti.sleep(2)

            self.changeDirection(True, "auto")
            ti.sleep(8)

            # print("Second")
            self.changeDirection(False, "auto")
            ti.sleep(2)

            self.changeDirection(True, "auto")
            ti.sleep(8)

            hopper_cmd = hopper_cmdL

            while True:  # auotmation loop. order to operation = Z -> Hopper -> Recoater
                try:
                    if self.pause_flag.value == True:
                        print("pAUSE")
                        ti.sleep(1)
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
                                if self.debug_var == 2:
                                    self.parent_connection.send("Hopper command change error")
                                # self.printToConsole("Hopper command change error")
                        except requests.exceptions.Timeout as e:
                            print(f"Hopper Request timed out. Connection could not be established.\n{e}")
                            self.parent_connection.send(
                                "Hopper Request timed out. Connection could not be established.")
                            # self.mainwindow_console_signal.emit("Hopper Request timed out. Connection could not be established.")
                        except requests.exceptions.RequestException as e:
                            print(f"An Hopper request error occurred: {e}")
                            self.parent_connection.send("An Hopper request error occurred:")
                            # self.mainwindow_console_signal.emit(f"An Hopper request error occurred: {e}")

                        ti.sleep(3)

                        # Move Recoater
                        self.changeDirection(False, "auto")
                        ti.sleep(1)
                        self.changeDirection(True, "auto")
                        ti.sleep(8)

                        try:
                            if self.debug_var == 2:
                                print("Moving z")
                                # self.mainwindow_console_signal.emit("Moving in Z direction")
                            req = requests.post(url=f"http://{self.api}/printer/gcode/script",
                                                params=move_z, timeout=2)
                            req.raise_for_status()
                        except requests.exceptions.Timeout:
                            print("Move Z Request timed out. Connection could not be established.")
                            self.parent_connection.send("Move Z Request timed out. Connection could not be established.")
                            # self.mainwindow_console_signal.emit("Hopper Request timed out. Connection could not be established.")
                        except requests.exceptions.RequestException as e:
                            print(f"A Z request error occurred: {e}")
                            self.parent_connection.send(f"A Z request error occurred: {e}")
                            # self.mainwindow_console_signal.emit(f"An Hopper request error occurred: {e}")
                        ti.sleep(5)

                except Exception as e:
                    print(f"Loop error\n {e}")
                    # self.mainwindow_console_signal.emit("Loop error")
                    continue
        except Exception as e:
            print("Auto process error \n {e}")
            # self.printToConsole("Auto process error")

    def environment_control(self):  # Function to handle the environment management process
        while True:
            self.environment_instance.update_screen()
            time.sleep(1)

    def Home_recoater(self):  # Function to home the recoater system
        self.home.setStyleSheet(self.current_style)
        if self.debug_var == 2:
            self.printToConsole("Homing recoater system")
        try:
            cmd = "Recoater_RV\r"
            if self.debug_var == 2:
                self.printToConsole(f"Command:{cmd}")
                print(f"Command:{cmd}")
            self.serial.serial_write(cmd)
        except Exception as e:
            print("Homing error \n {e}")
            self.printToConsole("Recoater Homing error")

    def recoater_emergency(self):  # Function to handing the emergency stoppage of the recoater system
        print("Emergency recoater stop initiated")
        self.printToConsole("Emergency recoater stop initiated")
        self.recoater_Estop.setStyleSheet(self.current_style)
        try:
            cmd = "Recoater_STOP_IN\r"
            self.serial.serial_write(cmd)

            time.sleep(1)

            cmd = "Roller_STOP_IN\r"
            self.serial.serial_write(cmd)
        except Exception as e:
            print("Recoater emergerncy stop errror \n {e}")
            self.printToConsole("Recoater emergency stop error")

    def printToConsole(self, text):  # Function to print the console in the UI
        # Add text to the console
        self.console.append("AMCOE/system/console$" + text)

    def printToSerialMonitor(self, text):  # Function to print the console in the UI
        # Add text to the console
        self.serial_monitor.append("AMCOE/system/console$" + text)

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
                    if val < 40 or val > 3150:
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
                self.parent_connection.send("Error")
            if self.debug_var == 2:
                print("Trying to open new serial port")
                if auto != "auto":
                    self.parent_connection.send("Trying to open new serial port")
                try:
                    self.serial.connect()
                except:
                    print("unable to establish serial communication")
                    if auto != "auto":
                        self.parent_connection.send("Trying to open new serial port")

    def start(self, motor_select):  # Function to handle the start of the motors
        try:
            if motor_select:  # Motor 1
                self.recoater.setStyleSheet(
                    self.current_style)  # this type of line in all functions is used for the click effect
                if self.serial.serial.is_open:
                    cmd = "Recoater_START\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        print("Debug statement")
                        self.printToConsole(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    self.printToConsole("Serial port is not open")

            else:  # Motor 2
                self.roller.setStyleSheet(self.current_style)
                if self.serial.serial.is_open:
                    cmd = "Roller_START\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        self.parent_connection.send(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    self.parent_connection.send("Serial port is not open")

        except Exception as e:
            print(f"start function Error\n {e}")
            self.parent_connection.send("Error")
            print("Trying to open new serial port")
            self.parent_connection.send("Trying to open new serial port")
            try:
                self.serial.open()
            except Exception as e:
                print(f"unable to establish serial communication due to \n {e}")
                self.printToConsole("unable to establish serial communication")

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
                        cmd = "Recoater_BRAKE\r"
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except:
                        print("Error in braking Motor 1")
                        self.printToConsole("Error in braking Motor 1")
                else:
                    self.Rbrake.setStyleSheet(self.current_style)  # R prefix indicated motor 2 / ROLLER
                    try:
                        cmd = "Roller_BRAKE\r"
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except:
                        print("Error in braking R Motor")
                        self.printToConsole("Error in braking R Motor")

            else:
                print("Unable to detect a serial connection")
                self.printToConsole("Unable to detect a serial connection")

        except Exception as e:
            print("Error in brake function \n {e}")
            self.printToConsole("Error in brake function")

    def instantStop(self,
                    motor_select):  # Function to instantaneously stop the motor, the buttons are not displayed in the GUI
        try:
            if self.serial.serial.is_open:
                if motor_select:
                    try:
                        cmd = "Recoater_STOP_IN\r"
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.printToConsole(f"COMMAND:{cmd}")
                        self.serial.serial_write(cmd)

                    except Exception as e:
                        print(f"Error in INSTANTANEOUSLY braking Motor 1 \n {e}")
                        self.printToConsole("Error in INSTANTANEOUSLY braking Motor 1")
                else:
                    try:
                        cmd = "Roller_STOP_IN\r"
                        print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in INSTANTANEOUSLY braking R Motor\n{e}")
                        self.printToConsole("Error in INSTANTANEOUSLY braking R Motor")

            else:
                print("Unable to detect a serial connection")
                self.printToConsole("Unable to detect a serial connection")

        except:
            print("Error in instant brake function")
            self.printToConsole("Error in instant brake function")

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
                            self.printToConsole(f"Command:{cmd}")
                            print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in DECELERATING brakes in Motor 1\n{e}")
                        self.printToConsole("Error in DECELERATING brakes in Motor 1")
                else:
                    self.RdecStop.setStyleSheet(self.current_style)
                    try:
                        cmd = "Roller_STOP_DC\r"
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                            print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in DECELERATING brakes in R Motor\n{e}")
                        self.printToConsole("Error in DECELERATING brakes in R Motor")

            else:
                print("Unable to detect a serial connection")
                self.printToConsole("Unable to detect a serial connection")

        except Exception as e:
            print(f"Error in decelerating brake function\n{e}")
            self.printToConsole("Error in decelerating brake function")

    def changeDirection(self, motor_select,
                        auto="0"):  # Function to handle the change of direction of motion of recoater motors
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
                            cmd = "Recoater_RV\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            MOTOR_DIR = False
                            if auto != "auto":
                                self.changeDIR.setText("Move Right")
                        else:
                            cmd = "Recoater_FW\r"
                            self.serial.serial_write(cmd)
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            MOTOR_DIR = True
                            if auto != "auto":
                                self.changeDIR.setText("Move left")
                    except Exception as e:
                        print(f"Error in changing direction of roation of Motor 1\n{e}")
                        if auto != "auto":
                            self.printToConsole("Error in changing direction of roation of Motor 1")

                else:
                    self.RchangeDIR.setStyleSheet(self.current_style)
                    try:
                        if RMOTOR_DIR:
                            cmd = "Roller_RV\r"
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")

                            print(f"command:{cmd}")
                            self.serial.serial_write(cmd)
                            RMOTOR_DIR = False
                            if auto != "auto":
                                self.RchangeDIR.setText("AntiClockwise")
                        else:
                            cmd = "Roller_FW\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            RMOTOR_DIR = True
                            if auto != "auto":
                                self.RchangeDIR.setText("Clockwise")
                    except Exception as e:
                        print(f"Error in changing direction of roation of Motor 2\n{e}")
                        if auto != "auto":
                            self.printToConsole("Error in changing direction of rotation of Motor 2")
            else:
                print("Serial port not open")
                if auto != "auto":
                    self.printToConsole("Serial port not open")

        except Exception as e:
            print("Error in the direction changing function\n{e}")
            if auto != "auto":
                self.printToConsole("Error in the direction changing function")


def main():
    app = QApplication([])
    parent_conn, child_conn = multiprocessing.Pipe()
    window = GUI(parent_conn, child_conn)
    app.exec_()


if __name__ == '__main__':
    main()
