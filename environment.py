import requests
import time


class Environment():
    def __init__(self, main_main):
        self.parent = main_main
        self.parent.C1_target.setText("")
        self.parent.C2_target.setText("")
        self.parent.C3_target.setText("")
        self.parent.B1_target.setText("")
        self.parent.B2_target.setText("")
        self.parent.HopL_target.setText("")
        self.parent.HopR_target.setText("")

    def update_screen(self):
        try:
            while True:
                #Testing tiva connection
                if self.parent.serial.is_open:
                    #print(self.serial.is_open)
                    self.parent.tiva_status.setText("Tiva Online")
                    self.parent.tiva_status.setStyleSheet("color: green")
                else:
                    self.parent.tiva_status.setText("Tiva Offline")
                    self.parent.tiva_status.setStyleSheet("color: red")

                try:
                    req = requests.get(url=f"http://{self.parent.api}/api/printer", params=self.parent.params, timeout=5)
                    req.raise_for_status()
                    req = req.json()
                except requests.exceptions.Timeout:
                    print("Environment Request timed out. Connection could not be established.")
                    #self.printToConsole("Environment Request timed out. Connection could not be established.")
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
                    #self.printToConsole(f"An error occurred: {e}")

                temperatures = req["temperature"]

                if req.raise_for_status == 200:
                    self.parent.MCU_Status.setText("MCU Online")
                    self.parent.MCU_Status.setStyleSheet("color: green")
                else:
                    self.parent.MCU_Status.setText("MCU Offline")
                    self.parent.MCU_Status.setStyleSheet("color: red")


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
        except:
            print("Environment update screen error")

    def set_target_temperature(self,select):
        if select == "C1":
            target = self.parent.C1_target.text()
            cmd = {
                "command": "target",
                "target": int(target)
            }
            try:
                req = requests.post(url=f"http://{self.parent.api}/api/printer/chamber", params=self.parent.params,json = cmd, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Chamber temp Request timed out. Connection could not be established.")
                #self.printToConsole("Environment Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
        elif select == "C2":
            pass
        elif select == "C3":
            pass
        elif select == "B1":
            target = self.parent.B1_target.text()
            cmd = {
                "command": "target",
                "target": int(target)
            }
            try:
                req = requests.post(url=f"http://{self.parent.api}/api/printer/bed", params=self.parent.params,json = cmd, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Bed temp Request timed out. Connection could not be established.")
                #self.printToConsole("Environment Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
        elif select == "B2":
            pass
        elif select == "Lhopper":
            pass
        else:
            pass


