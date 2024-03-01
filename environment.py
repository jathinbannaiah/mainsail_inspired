import requests
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QObject

#DONT UPDATE GUI ON CHILD PROCESSES AND THREADS

class Environment(QObject):
    status_signal = pyqtSignal(dict)
    def __init__(self, main_main):
        try:
            super().__init__()
            self.parent = main_main
            self.status = {}
            # self.parent.C1_target.setText("")
            # self.parent.C2_target.setText("")
            # self.parent.C3_target.setText("")
            # self.parent.B1_target.setText("")
            # self.parent.B2_target.setText("")
            # self.parent.HopL_target.setText("")
            # self.parent.HopR_target.setText("")
            self.flag = True
        except Exception as e:
            self.parent.parent_connection.send(f"Error E1: Error in environment.__init__()\n{e}")

    def run(self):
        try:
            print("Environment")
            status = self.update_screen()                  #Getting the data from the server
            if status:
                self.status_signal.emit(status)
            time.sleep(3)
        except Exception as e:
            self.parent.parent_connection.send(f"Error E2: Error in environment.run()\n{e}")

    def update_screen(self):
        try:
            req = ""
            temperatures = ""
            while True:
                #Testing tiva connection
                if self.parent.serial.serial.is_open:
                    #print(self.serial.is_open)
                    # self.parent.tiva_status.setText("Tiva Online")
                    # self.parent.tiva_status.setStyleSheet("color: green")
                    self.status["tiva"] = "Online"
                else:
                    # self.parent.tiva_status.setText("Tiva Offline")
                    # self.parent.tiva_status.setStyleSheet("color: red")
                    self.status["tiva"] = "Offline"

                try:
                    #req = requests.get(url=f"http://{self.parent.api}/api/printer", params=self.parent.params, timeout=2)
                    req = requests.get(url=f"http://{self.parent.api}/server/temperature_store?include_monitors=false",timeout=5)
                    req.raise_for_status()
                    req_data = req.json()
                    req_data = req_data['result']
                    for key in req_data:
                        temperatures = {key: req_data[key]['temperatures'][0]}

                    #temperatures = req_data["temperatures"]
                    if req.raise_for_status == 200:
                        # self.parent.MCU_Status.setText("MCU Online")
                        # self.parent.MCU_Status.setStyleSheet("color: green")
                        self.status["Octopus"] = "Online"
                        self.flag = True
                    else:
                        # self.parent.MCU_Status.setText("MCU Offline")
                        # self.parent.MCU_Status.setStyleSheet("color: red")
                        self.status["Octopus"] = "Offline"
                except requests.exceptions.Timeout as e:
                    if self.flag:
                        print("Environment Request timed out. Connection could not be established.")
                        self.parent.parent_connection.send(f"Error E3: Error in environment.update_screen()(Timeout)\n{e}")
                        self.flag = False
                except requests.exceptions.RequestException as e:
                    if self.flag:
                        print(f"An error occurred: {e}")
                        self.parent.parent_connection.send(f"Error E4: Error in environment.update_screen()(request)\n{e}")
                        self.flag = False

                self.status["Temperature_data"] = temperatures
                return_variable = self.status

                return return_variable


                # #Current Temperature
                # self.parent.C1_Temp.setText(str(temperatures["chamber"]["actual"]))
                # self.parent.C2_Temp.setText(str(temperatures["chamber"]["actual"]))
                # self.parent.C3_Temp.setText(str(temperatures["chamber"]["actual"]))
                # self.parent.B1_Temp.setText(str(temperatures["bed"]["actual"]))
                # self.parent.B2_Temp.setText(str(temperatures["bed"]["actual"]))
                # self.parent.HopL_Temp.setText(str(temperatures["tool0"]["actual"]))
                # self.parent.HopR_Temp.setText(str(temperatures["tool1"]["actual"]))
                #
                # #Heater state
                # if temperatures["chamber"]["actual"] < temperatures["chamber"]["target"]:
                #     self.parent.C1_state.setText("ON")
                #     self.parent.C2_state.setText("ON")
                #     self.parent.C3_state.setText("ON")
                # else:
                #     self.parent.C1_state.setText("OFF")
                #     self.parent.C2_state.setText("OFF")
                #     self.parent.C3_state.setText("OFF")
                #
                # if temperatures["bed"]["actual"] < temperatures["bed"]["target"]:
                #     self.parent.B1_state.setText("ON")
                #     self.parent.B2_state.setText("ON")
                #
                # else:
                #     self.parent.B1_state.setText("OFF")
                #     self.parent.B2_state.setText("OFF")
                #
                # if temperatures["tool0"]["actual"] < temperatures["tool0"]["target"]:
                #     self.parent.HopL_state.setText("ON")
                # else:
                #     self.parent.HopL_state.setText("OFF")
                #
                # if temperatures["tool1"]["actual"] < temperatures["tool1"]["target"]:
                #     self.parent.HopR_state.setText("ON")
                # else:
                #     self.parent.HopR_state.setText("OFF")

                #time.sleep(1)
        except Exception as e:
            if self.flag:
                 print(f"Environment update screen error\n{str(e)}")
                 self.parent.parent_connection.send(f"Error E5: Error in environment.update_screen()\n{e}")    # This is where the QtextCursor error is formed
                 #self.parent.parent_connection.send(69)        # Above error is fxed the first time and it failed afterwards
                 self.flag = False

    def set_target_temperature(self,select):
        if select == "C1":
            self.parent.C1_ok.setStyleSheet(self.parent.current_style)
            target = self.parent.C1_target.text()
            if target == "":
                target  = 25
            if int(target) > 350:
                self.parent.parent_connection.send("Invalid temperature value")
                return

            try:
                cmd = {
                    "command": "target",
                    "target": int(target)
                }
                req = requests.post(url=f"http://{self.parent.api}/api/printer/chamber", params=self.parent.params,json = cmd, timeout=2)
                req.raise_for_status()
            except requests.exceptions.Timeout as e:
                print("Chamber temp Request timed out. Connection could not be established.")
                self.parent.parent_connection.send(f"Error E6: Error in environment.set_target_temperature()(Timeout)\n{e}")
                #self.printToConsole("Environment Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                self.parent.parent_connection.send(f"Error E7: Error in environment.set_target_temperature()(C1)(request)\n{e}")
            except Exception as e:
                print(f"Invalid target\n{e}")
                self.parent.parent_connection.send(f"Error E8: Error in environment.set_target_temperature()(C1)(Invalid Target)\n{e}")
        elif select == "C2":
            self.parent.C2_ok.setStyleSheet(self.parent.current_style)
            target = self.parent.C2_target.text()
            if target == "":
                target  = 25
            if int(target) > 350:
                self.parent.parent_connection.send("Invalid temperature value")
                return

            try:
                cmd = {
                    "command": "target",
                    "target": int(target)                      #Make necessary changes for chamber 2
                }
                req = requests.post(url=f"http://{self.parent.api}/api/printer/chamber", params=self.parent.params,json = cmd, timeout=2)
                req.raise_for_status()
            except requests.exceptions.Timeout as e:
                print("Chamber temp Request timed out. Connection could not be established.")
                self.parent.parent_connection.send(f"Error E6: Error in environment.set_target_temperature()(Timeout)\n{e}")
                #self.printToConsole("Environment Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                self.parent.parent_connection.send(f"Error E12: Error in environment.set_target_temperature()(C2)(request)\n{e}")
            except Exception as e:
                print(f"Invalid target\n{e}")
                self.parent.parent_connection.send(f"Error E13: Error in environment.set_target_temperature()(C3)(Invalid Target)\n{e}")
        elif select == "B1":
            self.parent.B1_ok.setStyleSheet(self.parent.current_style)
            target = self.parent.B1_target.text()
            try:
                cmd = {
                    "command": "target",
                    "target": int(target)
                }
            except Exception as e:
                self.parent.parent_connection.send(f"Error E9: Error in environment.set_target_temperature()(Invalid target in B1)\n{e}")
                #self.parent.parent_connection.send("Invalid target")
            try:
                req = requests.post(url=f"http://{self.parent.api}/api/printer/bed", params=self.parent.params,json = cmd, timeout=2)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Bed temp Request timed out. Connection could not be established.")
                self.parent.parent_connection.send(f"Error E10: Error in environment.set_target_temperature()(Timeout at B1)\n{e}")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                self.parent.parent_connection.send(f"Error E11: Error in environment.set_target_temperature()(Request at B1)\n{e}")
        elif select == "B2":
            self.parent.B2_ok.setStyleSheet(self.parent.current_style)

        elif select == "B3":
            self.parent.B3_ok.setStyleSheet(self.parent.current_style)

        elif select == "B4":
            self.parent.B4_ok.setStyleSheet(self.parent.current_style)

        elif select == "B5":
            self.parent.B5_ok.setStyleSheet(self.parent.current_style)

        elif select == "B6":
            self.parent.B6_ok.setStyleSheet(self.parent.current_style)

        elif select == "Lhopper":
            self.parent.HopL_ok.setStyleSheet(self.parent.current_style)

        elif select == "Rhopper":
            self.parent.HopR_ok.setStyleSheet(self.parent.current_style)
        else:
            pass


