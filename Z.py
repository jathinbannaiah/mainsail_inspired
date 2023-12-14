import requests
import time
from PyQt5.QtCore import QObject, pyqtSignal


class Zmotion(QObject):
    console_sig = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.main = parent

    def Zaxis_up(self, object):
        pass

    def Zaxis_down(self, object):
        pass

    def Z_Up(self):
        try:
            move_z = {
                "script": "move_Z10"
            }
            try:
                print("Moving z")
                req = requests.post(url=f"http://{self.main.api}/printer/gcode/script", params=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Move Z Request timed out. Connection could not be established.")
                self.console_sig.emit("Move Z Request timed out. Connection could not be established.")
                # self.printToConsole("Hopper Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"A Z request error occurred: {e}")
                self.console_sig.emit(f"A Z request error occurred: {e}")
                # self.printToConsole(f"An Hopper request error occurred: {e}"
            time.sleep(5)
        except Exception as e:
            print("Error in Z function \n {e}")
            self.console_sig.emit("Error in Z function \n {e}")
            # self.printToConsole("Error in Dose function")

    def set_distance(self, button):
        pass

    def Z_Down(self):
        try:
            move_z = {
                "script": "move_Z10"
            }
            try:
                print("Moving z")
                req = requests.post(url=f"http://{self.main.api}/printer/gcode/script", params=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Move Z Request timed out. Connection could not be established.")
                self.console_sig.emit("Move Z Request timed out. Connection could not be established.")
                # self.printToConsole("Hopper Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"A Z request error occurred: {e}")
                self.console_sig.emit(f"A Z request error occurred: {e}")
                # self.printToConsole(f"An Hopper request error occurred: {e}"
            time.sleep(5)
        except Exception as e:
            print("Error in Z function \n {e}")
            self.console_sig.emit("Error in Z function \n {e}")
            # self.printToConsole("Error in Dose function")
