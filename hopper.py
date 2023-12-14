import requests
import time
from PyQt5.QtCore import QObject, pyqtSignal


class Hopper(QObject):
    console_signal = pyqtSignal(str)
    def __init__(self, hopper):
        super().__init__()
        self.mainHopperInstance = hopper
        self.base_timeSelect_style = "border:1px solid rgb(0,0,0);\nborder-radius:5px;\ncolor: rgb(170, 170, 170);\nbackground-color: rgb(85, 85, 85);"
        self.opening_time = ""
        self.opening_distance = ""
        self.hopper_select = ""



    def select(self, selection):
        if selection == "L":
            #self.mainHopperInstance.Lhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 170, 255);")

            self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
            current_style = self.mainHopperInstance.Lhopper.styleSheet()
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = "border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);"
                self.hopper_select = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.hopper_select = "left"
            self.mainHopperInstance.Lhopper.setStyleSheet(style)

        else:
            #self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")

            self.mainHopperInstance.Lhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 170, 255);")
            current_style = self.mainHopperInstance.Rhopper.styleSheet()
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = "border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);"
                self.hopper_select = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.hopper_select = "right"
            self.mainHopperInstance.Rhopper.setStyleSheet(style)

    def timeSelect(self, time):
        print(time)
        if time == 1:
            current_style = self.mainHopperInstance.Hopper1sec.styleSheet()
            self.mainHopperInstance.Hopper3sec.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper5sec.setStyleSheet(self.base_timeSelect_style)
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = self.base_timeSelect_style
                self.opening_time = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.opening_time = time
            self.mainHopperInstance.Hopper1sec.setStyleSheet(style)

        elif time == 3:
            current_style = self.mainHopperInstance.Hopper3sec.styleSheet()
            self.mainHopperInstance.Hopper1sec.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper5sec.setStyleSheet(self.base_timeSelect_style)
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = self.base_timeSelect_style
                self.opening_time = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.opening_time = time
            self.mainHopperInstance.Hopper3sec.setStyleSheet(style)
        else:
            current_style = self.mainHopperInstance.Hopper5sec.styleSheet()
            self.mainHopperInstance.Hopper3sec.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper1sec.setStyleSheet(self.base_timeSelect_style)
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = self.base_timeSelect_style
                self.opening_time = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.opening_time = time
            self.mainHopperInstance.Hopper5sec.setStyleSheet(style)

    def openingSelect(self, distance):
        print(distance)
        if distance == 1:
            current_style = self.mainHopperInstance.Hopper1mm.styleSheet()
            self.mainHopperInstance.Hopper5mm.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper10mm.setStyleSheet(self.base_timeSelect_style)
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = self.base_timeSelect_style
                self.opening_distance = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.opening_distance = distance
            self.mainHopperInstance.Hopper1mm.setStyleSheet(style)

        elif distance == 5:
            current_style = self.mainHopperInstance.Hopper5mm.styleSheet()
            self.mainHopperInstance.Hopper1mm.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper10mm.setStyleSheet(self.base_timeSelect_style)
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = self.base_timeSelect_style
                self.opening_distance = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.opening_distance = distance
            self.mainHopperInstance.Hopper5mm.setStyleSheet(style)
        else:
            current_style = self.mainHopperInstance.Hopper10mm.styleSheet()
            self.mainHopperInstance.Hopper5mm.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper1mm.setStyleSheet(self.base_timeSelect_style)
            if " border: 3px solid rgb(0,255,0)" in current_style:
                style = self.base_timeSelect_style
                self.opening_distance = ""
            else:
                style = current_style + "\n border: 3px solid rgb(0,255,0);"
                self.opening_distance = distance
            self.mainHopperInstance.Hopper10mm.setStyleSheet(style)

    def Dose(self,api,params):
        self.mainHopperInstance.Hopper_Dose.setStyleSheet(self.mainHopperInstance.current_style)

        if self.opening_time != "" and self.opening_distance != "" and self.hopper_select != "":
            if self.hopper_select == "left":
                hopper_cmdL = {
                    "script": "move_hopper_left"
                }
                try:
                    req = requests.post(url=f"http://{self.mainHopperInstance.api}/printer/gcode/script", params=hopper_cmdL,
                                        timeout=2)
                    if req.raise_for_status() == 200:
                        if self.parent.debug_var == 2:
                            print("Left hopper command successful")
                            self.console_signal.emit("Left hopper command successful")
                        self.mainHopperInstance.Lhopper_status.setText("Open")
                        time.sleep(self.opening_time)
                        self.mainHopperInstance.Lhopper_status.setText("closed")
                    else:
                        if self.parent.debug_var == 2:
                            print("Left hopper command failed")
                            self.mainHopperInstance.parent_connection.send("Left hopper command failed")


                except requests.exceptions.Timeout:
                    print("Left Hopper Request timed out. Connection could not be established.")
                    self.console_signal.emit("Left Hopper Request timed out. Connection could not be established.")
                except requests.exceptions.RequestException as e:
                    print(f"An Hopper request error occurred: {e}")
                    self.console_signal.emit(f"An Hopper request error occurred: {e}")
                except Exception as e:
                    print("Error in Dose function \n {e}")
                    self.mainHopperInstance.parent_connection.send("Left hopper command failed")
            else:
                hopper_cmdR = {
                    "script": "move_hopper_right"
                }
                try:
                    req = requests.post(url=f"http://{self.mainHopperInstance.api}/printer/gcode/script", params=hopper_cmdR,
                                        timeout=2)
                    req.raise_for_status()
                    if req.raise_for_status() == 200:
                        if self.parent.debug_var == 2:
                            print("Left hopper command failed")
                            self.console_signal.emit("Left hopper command failed")
                        self.mainHopperInstance.Rhopper_status.setText("Open")
                        time.sleep(self.opening_time)
                        self.mainHopperInstance.Rhopper_status.setText("closed")
                    else:
                        if self.parent.debug_var == 2:
                            print("Right hopper command failed")
                            self.console_signal.emit("Right hopper command failed")

                except requests.exceptions.Timeout:
                    print("Right Hopper Request timed out. Connection could not be established.")
                    self.mainHopperInstance.parent_connection.send("Right Hopper Request timed out. Connection could not be established.")
                except requests.exceptions.RequestException as e:
                    print(f"An Hopper request error occurred: {e}")
                    self.console_signal.emit(f"An Hopper request error occurred: {e}")
                except Exception as e:
                    print("Error in Dose function \n {e}")
                    self.mainHopperInstance.parent_connection.send("Error in Dose function")
        else:
            if self.hopper_select == "":
                print("Please select a hopper")
                self.console_signal.emit("Please select a hopper")
            if self.opening_time == "":
                print("Please select the required openning time")
                self.console_signal.emit("Please select the required openning time")
            if self.opening_distance == "":
                print("Please selct the required opeening distance")
                self.console_signal.emit("Please select the required opeening distance")

        self.mainHopperInstance.Lhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 170, 255);")
        self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
        self.mainHopperInstance.Hopper10mm.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper5mm.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper1mm.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper1sec.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper3sec.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper5sec.setStyleSheet(self.base_timeSelect_style)
