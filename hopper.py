import requests
import time


class Hopper:
    def __init__(self, hopper):
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
                style = "border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 170, 255);"
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

        if self.opening_time != "" and self.opening_distance != "" and self.hopper_select != "":
            if self.hopper_select == "left":
                hopper_cmdL = {
                    "command": "move_hopper_left"
                }
                try:
                    req = requests.post(url=f"http://{self.mainHopperInstance.api}/api/printer/command", params=self.mainHopperInstance.params, json=hopper_cmdL,
                                        timeout=5)
                    if req.raise_for_status() == 200:
                        print("Left hopper command successful")
                        self.mainHopperInstance.Lhopper_status.setText("Open")
                        time.sleep(self.opening_time)
                        self.mainHopperInstance.Lhopper_status.setText("closed")
                    else:
                        print("Left hopper command failed")


                except requests.exceptions.Timeout:
                    print("Hopper Request timed out. Connection could not be established.")
                    # self.printToConsole("Hopper Request timed out. Connection could not be established.")
                except requests.exceptions.RequestException as e:
                    print(f"An Hopper request error occurred: {e}")
            else:
                hopper_cmdR = {
                    "command": "move_hopper_right"
                }
                try:
                    req = requests.post(url=f"http://{self.api}/api/printer/command", params=self.params, json=hopper_cmdR,
                                        timeout=5)
                    req.raise_for_status()
                    if req.raise_for_status() == 200:
                        print("Left hopper command successful")
                        self.mainHopperInstance.Rhopper_status.setText("Open")
                        time.sleep(self.opening_time)
                        self.mainHopperInstance.Rhopper_status.setText("closed")
                    else:
                        print("Right hopper command failed")

                except requests.exceptions.Timeout:
                    print("Hopper Request timed out. Connection could not be established.")
                    # self.printToConsole("Hopper Request timed out. Connection could not be established.")
                except requests.exceptions.RequestException as e:
                    print(f"An Hopper request error occurred: {e}")
        else:
            if self.hopper_select == "":
                print("Please select a hopper")
            if self.opening_time == "":
                print("Please select the required openning time")
            if self.opening_distance == "":
                print("Please selct the required opeening distance")

        self.mainHopperInstance.Lhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 170, 255);")
        self.mainHopperInstance.Rhopper.setStyleSheet("border-radius:5px;\ncolor: rgb(255, 255, 255);\nbackground-color: rgb(0, 97, 145);")
        self.mainHopperInstance.Hopper10mm.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper5mm.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper1mm.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper1sec.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper3sec.setStyleSheet(self.base_timeSelect_style)
        self.mainHopperInstance.Hopper5sec.setStyleSheet(self.base_timeSelect_style)
