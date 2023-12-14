import requests
import time


class Environment:
    def __init__(self, main_main):
        self.parent = main_main
        self.parent.C1_target.setText("")
        self.parent.C2_target.setText("")
        self.parent.C3_target.setText("")
        self.parent.B1_target.setText("")
        self.parent.B2_target.setText("")
        self.parent.HopL_target.setText("")
        self.parent.HopR_target.setText("")
        self.flag = True

    def update_screen(self):
        try:
            req = ""
            temperatures = ""
            while True:
                #Testing tiva connection
                if self.parent.serial.serial.is_open:
                    #print(self.serial.is_open)
                    self.parent.tiva_status.setText("Tiva Online")
                    self.parent.tiva_status.setStyleSheet("color: green")
                else:
                    self.parent.tiva_status.setText("Tiva Offline")
                    self.parent.tiva_status.setStyleSheet("color: red")

                try:
                    req = requests.get(url=f"http://{self.parent.api}/api/printer", params=self.parent.params, timeout=2)
                    req.raise_for_status()
                    req = req.json()
                    temperatures = req["temperature"]
                    if req.raise_for_status == 200:
                        self.parent.MCU_Status.setText("MCU Online")
                        self.parent.MCU_Status.setStyleSheet("color: green")
                        self.flag = True
                    else:
                        self.parent.MCU_Status.setText("MCU Offline")
                        self.parent.MCU_Status.setStyleSheet("color: red")
                except requests.exceptions.Timeout:
                    if self.flag:
                        print("Environment Request timed out. Connection could not be established.")
                        self.parent.parent_connection.send("Environment Request timed out. Connection could not be established.")
                        self.flag = False
                except requests.exceptions.RequestException as e:
                    if self.flag:
                        print(f"An error occurred: {e}")
                        self.parent.parent_connection.send(f"An error occurred: {e}")
                        self.flag = False


                #Current Temperature
                self.parent.C1_Temp.setText(str(temperatures["chamber"]["actual"]))
                self.parent.C2_Temp.setText(str(temperatures["chamber"]["actual"]))
                self.parent.C3_Temp.setText(str(temperatures["chamber"]["actual"]))
                self.parent.B1_Temp.setText(str(temperatures["bed"]["actual"]))
                self.parent.B2_Temp.setText(str(temperatures["bed"]["actual"]))
                self.parent.HopL_Temp.setText(str(temperatures["tool0"]["actual"]))
                self.parent.HopR_Temp.setText(str(temperatures["tool1"]["actual"]))

                #Heater state
                if temperatures["chamber"]["actual"] < temperatures["chamber"]["target"]:
                    self.parent.C1_state.setText("ON")
                    self.parent.C2_state.setText("ON")
                    self.parent.C3_state.setText("ON")
                else:
                    self.parent.C1_state.setText("OFF")
                    self.parent.C2_state.setText("OFF")
                    self.parent.C3_state.setText("OFF")

                if temperatures["bed"]["actual"] < temperatures["bed"]["target"]:
                    self.parent.B1_state.setText("ON")
                    self.parent.B2_state.setText("ON")

                else:
                    self.parent.B1_state.setText("OFF")
                    self.parent.B2_state.setText("OFF")

                if temperatures["tool0"]["actual"] < temperatures["tool0"]["target"]:
                    self.parent.HopL_state.setText("ON")
                else:
                    self.parent.HopL_state.setText("OFF")

                if temperatures["tool1"]["actual"] < temperatures["tool1"]["target"]:
                    self.parent.HopR_state.setText("ON")
                else:
                    self.parent.HopR_state.setText("OFF")

                time.sleep(1)
        except Exception as e:
            if self.flag:
                 print(f"Environment update screen error\n{e}")
                 self.parent.parent_connection.send("Environment update screen error")
                 self.flag = False

    def set_target_temperature(self,select):
        if select == "C1":
            self.parent.C1_ok.setStyleSheet(self.parent.current_style)
            target = self.parent.C1_target.text()
            try:
                cmd = {
                    "command": "target",
                    "target": int(target)
                }
                req = requests.post(url=f"http://{self.parent.api}/api/printer/chamber", params=self.parent.params,json = cmd, timeout=2)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Chamber temp Request timed out. Connection could not be established.")
                self.parent.parent_connection.send("Chamber temp Request timed out. Connection could not be established.")
                #self.printToConsole("Environment Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                self.parent.parent_connection.send(f"An error occurred: {e}")
            except Exception as e:
                print(f"Invalid target\n{e}")
                self.parent.parent_connection.send("Invalid target")
        elif select == "C2":
            pass
        elif select == "C3":
            pass
        elif select == "B1":
            self.parent.B1_ok.setStyleSheet(self.parent.current_style)
            target = self.parent.B1_target.text()
            try:
                cmd = {
                    "command": "target",
                    "target": int(target)
                }
            except Exception as e:
                print(f"Invalid target\n{e}")
                self.parent.parent_connection.send("Invalid target")
            try:
                req = requests.post(url=f"http://{self.parent.api}/api/printer/bed", params=self.parent.params,json = cmd, timeout=2)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Bed temp Request timed out. Connection could not be established.")
                self.parent.parent_connection.send("Environment Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                self.parent.parent_connection.send(f"An error occurred: {e}")
        elif select == "B2":
            pass
        elif select == "Lhopper":
            pass
        else:
            pass


