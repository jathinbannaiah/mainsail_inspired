import requests
import time
from PyQt5.QtCore import QObject, pyqtSignal


class Hopper(QObject):
    console_signal = pyqtSignal(str)
    def __init__(self, hopper):
        try:
            super().__init__()
            self.mainHopperInstance = hopper
            self.base_timeSelect_style = "border:1px solid rgb(0,0,0);\nborder-radius:5px;\ncolor: rgb(170, 170, 170);\nbackground-color: rgb(85, 85, 85);"
            self.opening_time = ""
            self.opening_distance = ""
            self.hopper_select = ""
            self.Lclicked = False
            self.Rclicked = False
        except Exception as e:
            self.mainHopperInstance.parent_connection.send(f"Error H1: Error in hopper.__init__()\n{e}")



    def select(self, selection):
        try:
            if selection == "L":
                self.Rclicked = False
                self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
                current_style = self.mainHopperInstance.Lhopper.styleSheet()
                if self.Lclicked:
                    self.mainHopperInstance.Lhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
                    self.Lclicked = False
                else:
                    if self.hopper_select == "":
                        self.hopper_select = "left"
                    else:
                        self.hopper_select = ""
                    self.Lclicked = True
                # if " border: 3px solid rgb(0,255,0)" in current_style:
                #     style = "border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);"
                #     self.hopper_select = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"   #Because ganesh did not want green border
                #self.mainHopperInstance.Lhopper.setStyleSheet(style)

            else:
                #self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
                self.Lclicked = False
                self.mainHopperInstance.Lhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
                current_style = self.mainHopperInstance.Rhopper.styleSheet()
                if self.Rclicked:
                    self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
                    self.Rclicked = False
                else:
                    if self.hopper_select == "":
                        self.hopper_select = "right"
                    else:
                        self.hopper_select = ""
                    self.Rclicked = True
                # if " border: 3px solid rgb(0,255,0)" in current_style:
                #     style = "border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);"
                #     self.hopper_select = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"
                #     self.hopper_select = "right"
                #self.mainHopperInstance.Rhopper.setStyleSheet(style)
        except Exception as e:
            self.mainHopperInstance.parent_connection.send(f"Error H2: Error in hopper.select()\n{e}")

    def timeSelect(self, time):
        print(time)
        try:
            if self.opening_time == time:
                self.opening_time = ""
            else:
                self.opening_time = time

            if time == 1:
                current_style = self.mainHopperInstance.Hopper1sec.styleSheet()
                self.mainHopperInstance.Hopper3sec.setStyleSheet(self.base_timeSelect_style)
                self.mainHopperInstance.Hopper5sec.setStyleSheet(self.base_timeSelect_style)
                # if self.opening_time == time:
                #     style = self.base_timeSelect_style
                #     self.opening_time = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"
                #     self.opening_time = time
                # self.mainHopperInstance.Hopper1sec.setStyleSheet(style)

            elif time == 3:
                current_style = self.mainHopperInstance.Hopper3sec.styleSheet()
                self.mainHopperInstance.Hopper1sec.setStyleSheet(self.base_timeSelect_style)
                self.mainHopperInstance.Hopper5sec.setStyleSheet(self.base_timeSelect_style)
                # if " border: 3px solid rgb(0,255,0)" in current_style:
                #     style = self.base_timeSelect_style
                #     self.opening_time = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"
                #     self.opening_time = time
                # self.mainHopperInstance.Hopper3sec.setStyleSheet(style)
            else:
                current_style = self.mainHopperInstance.Hopper5sec.styleSheet()
                self.mainHopperInstance.Hopper3sec.setStyleSheet(self.base_timeSelect_style)
                self.mainHopperInstance.Hopper1sec.setStyleSheet(self.base_timeSelect_style)
                # if " border: 3px solid rgb(0,255,0)" in current_style:
                #     style = self.base_timeSelect_style
                #     self.opening_time = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"
                #     self.opening_time = time
                # self.mainHopperInstance.Hopper5sec.setStyleSheet(style)
        except Exception as e:
            self.mainHopperInstance.parent_connection.send(f"Error H3: Error in hopper.timeSelect()\n{e}")

    def openingSelect(self, distance):
        print(distance)
        try:
            if self.opening_distance == distance:
                self.opening_distance = ""
            else:
                self.opening_distance = distance
            if distance == 1:
                current_style = self.mainHopperInstance.Hopper1mm.styleSheet()
                self.mainHopperInstance.Hopper5mm.setStyleSheet(self.base_timeSelect_style)
                self.mainHopperInstance.Hopper10mm.setStyleSheet(self.base_timeSelect_style)
                # if " border: 3px solid rgb(0,255,0)" in current_style:
                #     style = self.base_timeSelect_style
                #     self.opening_distance = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"
                #     self.opening_distance = distance
                # self.mainHopperInstance.Hopper1mm.setStyleSheet(style)

            elif distance == 5:
                current_style = self.mainHopperInstance.Hopper5mm.styleSheet()
                self.mainHopperInstance.Hopper1mm.setStyleSheet(self.base_timeSelect_style)
                self.mainHopperInstance.Hopper10mm.setStyleSheet(self.base_timeSelect_style)
                # if " border: 3px solid rgb(0,255,0)" in current_style:
                #     style = self.base_timeSelect_style
                #     self.opening_distance = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"
                #     self.opening_distance = distance
                # self.mainHopperInstance.Hopper5mm.setStyleSheet(style)
            else:
                current_style = self.mainHopperInstance.Hopper10mm.styleSheet()
                self.mainHopperInstance.Hopper5mm.setStyleSheet(self.base_timeSelect_style)
                self.mainHopperInstance.Hopper1mm.setStyleSheet(self.base_timeSelect_style)
                # if " border: 3px solid rgb(0,255,0)" in current_style:
                #     style = self.base_timeSelect_style
                #     self.opening_distance = ""
                # else:
                #     style = current_style + "\n border: 3px solid rgb(0,255,0);"
                #     self.opening_distance = distance
                # self.mainHopperInstance.Hopper10mm.setStyleSheet(style)
        except Exception as e:
            self.mainHopperInstance.parent_connection.send(f"Error H4: Error in hopper.openingSelect()\n{e}")

    def Dose(self,api,params):
        try:
            self.mainHopperInstance.Hopper_Dose.setStyleSheet(self.mainHopperInstance.current_style)
        except Exception as e:
            self.mainHopperInstance.parent_connection.send(f"Error H5: Error in hopper.Dose()(Stylesheet)\n{e}")

        if self.opening_time != "" and self.opening_distance != "" and self.hopper_select != "":
            if self.hopper_select == "left":
                hopper_cmdL = {
                    "script": "move_hopper_left"
                }
                try:
                    req = requests.post(url=f"http://{self.mainHopperInstance.api}/printer/gcode/script", params=hopper_cmdL,
                                        timeout=2)
                    if req.raise_for_status() == 200:
                        if self.mainHopperInstance.debug_var == 2:
                            print("Left hopper command successful")
                            #self.console_signal.emit("Left hopper command successful")
                            self.mainHopperInstance.parent_connection.send(f"Left hopper command successful")
                        self.mainHopperInstance.Lhopper_status.setText("Open")
                        time.sleep(self.opening_time)
                        self.mainHopperInstance.Lhopper_status.setText("closed")
                    else:
                        if self.mainHopperInstance.debug_var == 2:
                            print("Left hopper command failed")
                            self.mainHopperInstance.parent_connection.send("Left hopper command failed")


                except requests.exceptions.Timeout:
                    print("Left Hopper Request timed out. Connection could not be established.")
                    #self.console_signal.emit("Left Hopper Request timed out. Connection could not be established.")
                    self.mainHopperInstance.parent_connection.send(f"Error H6: Error in hopper.Dose()(Timeout)\n{e}")
                except requests.exceptions.RequestException as e:
                    print(f"An Hopper request error occurred: {e}")
                    #self.console_signal.emit(f"An Hopper request error occurred: {e}")
                    self.mainHopperInstance.parent_connection.send(f"Error H5: Error in hopper.Dose()(request)\n{e}")
                except Exception as e:
                    print("Error in Dose function \n {e}")
                    self.mainHopperInstance.parent_connection.send(f"Error H6: Error in hopper.Dose()\n{e}")
            else:
                hopper_cmdR = {
                    "script": "move_hopper_right"
                }
                try:
                    req = requests.post(url=f"http://{self.mainHopperInstance.api}/printer/gcode/script", params=hopper_cmdR,
                                        timeout=2)
                    req.raise_for_status()
                    if req.raise_for_status() == 200:
                        if self.mainHopperInstance.debug_var == 2:
                            print("right hopper command successful")
                            #self.console_signal.emit("Left hopper command failed")
                            self.mainHopperInstance.parent_connection.send(f"Right hopper command successful")

                        self.mainHopperInstance.Rhopper_status.setText("Open")
                        time.sleep(self.opening_time)
                        self.mainHopperInstance.Rhopper_status.setText("closed")
                    else:
                        if self.mainHopperInstance.debug_var == 2:
                            print("Right hopper command failed")
                            #self.console_signal.emit("Right hopper command failed")
                            self.mainHopperInstance.parent_connection.send(f"Right hopper command failed")


                except requests.exceptions.Timeout as e:
                    print("Right Hopper Request timed out. Connection could not be established.")
                    self.mainHopperInstance.parent_connection.send(f"Error H7: Error in hopper.Dose()(Timeout)(Right Hopper)\n{e}")
                except requests.exceptions.RequestException as e:
                    print(f"An Hopper request error occurred: {e}")
                    #self.console_signal.emit(f"An Hopper request error occurred: {e}")
                    self.mainHopperInstance.parent_connection.send(f"Error H8: Error in hopper.Dose()(request)(Right Hopper)\n{e}")
                except Exception as e:
                    print("Error in Dose function \n {e}")
                    #self.mainHopperInstance.parent_connection.send("Error in Dose function")
                    self.mainHopperInstance.parent_connection.send(f"Error H9: Error in hopper.Dose()(Right Hopper)\n{e}")
        else:
            if self.hopper_select == "":
                print("Please select a hopper")
                #self.console_signal.emit("Please select a hopper")
                self.mainHopperInstance.parent_connection.send("Please select a hopper and try again")
            if self.opening_time == "":
                print("Please select the required opening time")
                #self.console_signal.emit("Please select the required openning time")
                self.mainHopperInstance.parent_connection.send("Please select the required opening time and try again")
            if self.opening_distance == "":
                print("Please select the required opening distance")
                #self.console_signal.emit("Please select the required opeening distance")
                self.mainHopperInstance.parent_connection.send("Please select the required opening distance and try again")

        self.opening_time = ""
        self.opening_distance = ""
        self.hopper_select = ""
        self.Lclicked = False
        self.Rclicked =False

        try:
            self.mainHopperInstance.Lhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
            self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
            self.mainHopperInstance.Hopper10mm.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper5mm.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper1mm.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper1sec.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper3sec.setStyleSheet(self.base_timeSelect_style)
            self.mainHopperInstance.Hopper5sec.setStyleSheet(self.base_timeSelect_style)
        except Exception as e:
            self.mainHopperInstance.parent_connection.send(f"Error H10: Error in hopper.Dose()(Right Hopper)(Styling)\n{e}")


    def test_function(self, event):
        print("Hello, I am under the water, Please help me")
