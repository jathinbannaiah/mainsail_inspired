import requests
import time
from PyQt5.QtCore import QObject, pyqtSignal

Z_DEFAULT_DISTANCE = 10
Z_DEFAULT_VELOCITY = 100
Z_DEFAULT_OFFSET = 2

class Zmotion(QObject):
    console_sig = pyqtSignal(str)

    def __init__(self, parent):
        try:
            super().__init__()
            self.main = parent
        except Exception as e:
            self.main.parent_connection.send(f"Error Z0: Error in Z.__init__()\n{e}")

    def Zaxis_direct(self):
        pass

    def Zaxis_move_up(self):
        print("hi")
        try:
            try:
                self.main.Zaxis_up.setStyleSheet(self.main.current_style)
            except Exception as e:
                self.main.parent_connection.send(f"Error Z9: Error in Z.Zaxis_up()(Stylesheet)\n{e}")

            if self.main.z_distance.text():
                try:
                    z_distance_temp = float(self.main.z_distance.text())
                except ValueError as e:
                    self.main.parent_connection.send(f"Error Z6: Error in Z.Zaxis_up()(z_distance ValueError)\n{e}")
            else:
                z_distance_temp = Z_DEFAULT_DISTANCE
            if self.main.z_velocity.text():
                try:
                    z_vel_temp = float(self.main.z_velocity.text())
                except ValueError as e:
                    self.main.parent_connection.send(f"Error Z6: Error in Z.Zaxis_up()(z_velocity ValueError)\n{e}")
            else:
                z_vel_temp = Z_DEFAULT_VELOCITY
            if self.main.z_offset.text():
                try:
                    z_offset_temp = float(self.main.z_offset.text())
                except ValueError as e:
                    self.main.parent_connection.send(f"Error Z8: Error in Z.Zaxis_up()(z_offset ValueError)\n{e}")
            else:
                z_offset_temp = Z_DEFAULT_OFFSET

            try:
                move_z = {
                    "script": "FORCE_MOVE stepper=stepper_z distance=-0.1 velocity=2"
                }
                print("Moving z axis")
                req = requests.post(url=f"http://{self.main.api}/printer/gcode/script", params=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Z axis UP Request timed out. Connection could not be established.")
                #self.console_sig.emit("Move Z Request timed out. Connection could not be established.")
                self.main.parent_connection.send(f"Error Z10: Z axis UP  Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"Z axis UP  request error occurred: {e}")
                #self.console_sig.emit(f"A Z request error occurred: {e}")
                self.main.parent_connection.send(f"Error Z11: Error in Z.Z_Up(request)\n{e}")


        except Exception as e:
            self.main.parent_connection.send(f"Error Z1: Error in Z.Zaxis_up()\n{e}")

    def Zaxis_move_down(self):
        print("hi")
        try:
            self.main.Zaxis_down.setStyleSheet(self.main.current_style)
            try:
                self.main.Zaxis_up.setStyleSheet(self.main.current_style)
            except Exception as e:
                self.main.parent_connection.send(f"Error Z12: Error in Z.Zaxis_down()(Stylesheet)\n{e}")

            if self.main.z_distance.text():
                try:
                    z_distance_temp = float(self.main.z_distance.text())
                except ValueError as e:
                    self.main.parent_connection.send(f"Error Z13: Error in Z.Zaxis_down()(z_distance ValueError)\n{e}")
            else:
                z_distance_temp = Z_DEFAULT_DISTANCE
            if self.main.z_velocity.text():
                try:
                    z_vel_temp = float(self.main.z_velocity.text())
                except ValueError as e:
                    self.main.parent_connection.send(f"Error Z14: Error in Z.Zaxis_down()(z_velocity ValueError)\n{e}")
            else:
                z_vel_temp = Z_DEFAULT_VELOCITY
            if self.main.z_offset.text():
                try:
                    z_offset_temp = float(self.main.z_offset.text())
                except ValueError as e:
                    self.main.parent_connection.send(f"Error Z15: Error in Z.Zaxis_down()(z_offset ValueError)\n{e}")
            else:
                z_offset_temp = Z_DEFAULT_OFFSET

            try:
                move_z = {
                    "script": "G1 Z0.1 "                   #FORCE_MOVE stepper=stepper_z distance=0.1 velocity=2"
                }
                print("Moving z axis")
                req = requests.post(url=f"http://{self.main.api}/printer/gcode/script", params=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Z axis DOWN Request timed out. Connection could not be established.")
                #self.console_sig.emit("Move Z Request timed out. Connection could not be established.")
                self.main.parent_connection.send(f"Error Z16: Z axis DOWN  Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"Z axis UP  request error occurred: {e}")
                #self.console_sig.emit(f"A Z request error occurred: {e}")
                self.main.parent_connection.send(f"Error Z17: Error in Z.Z_down(request)\n{e}")
        except Exception as e:
            self.main.parent_connection.send(f"Error Z2: Error in Z.Zaxis_down()\n{e}")

    def Z_Up(self):
        try:
            try:
                self.main.Zstage_up.setStyleSheet(self.main.current_style)
            except Exception as e:
                self.main.parent_connection.send(f"Error Z18: Error in Z.Z_Up()(Stylesheet)\n{e}")
            move_z = {
                "script": "G1 Z-0.1"
            }
            try:
                print("Moving z")
                req = requests.post(url=f"http://{self.main.api}/printer/gcode/script", params=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Z dock Request timed out. Connection could not be established.")
                #self.console_sig.emit("Move Z Request timed out. Connection could not be established.")
                self.main.parent_connection.send(f"Error Z3: Move Z Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"A Z dock request error occurred: {e}")
                #self.console_sig.emit(f"A Z request error occurred: {e}")
                self.main.parent_connection.send(f"Error Z4: Error in Z.Z_Up(request)\n{e}")
            #time.sleep(1)
        except Exception as e:
            print(f"Error in Z function \n {e}")
            #self.console_sig.emit(f"Error in Z function \n {e}")
            self.main.parent_connection.send(f"Error Z4: Error in Z.Z_Up.\n{e}")
            # self.printToConsole("Error in Dose function")

    def set_distance(self, button):
        pass

    def Z_Down(self):
        try:
            try:
                self.main.Zstage_down.setStyleSheet(self.main.current_style)
            except Exception as e:
                self.main.parent_connection.send(f"Error Z18: Error in Z.Z_Down()(Stylesheet)\n{e}")
            move_z = {
                "script": "G28 Z0"
            }
            try:
                print("Moving z")
                req = requests.post(url=f"http://{self.main.api}/printer/gcode/script", params=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout as e:
                print("Move Z Undock Request timed out. Connection could not be established.")
                #self.console_sig.emit("Move Z Request timed out. Connection could not be established.")
                self.main.parent_connection.send(f"Error Z5: Error in Z.Z_Down(Timeout).\n{e}")

            except requests.exceptions.RequestException as e:
                print(f"A Z undock request error occurred: {e}")
                #self.console_sig.emit(f"A Z request error occurred: {e}")
                self.main.parent_connection.send(f"Error Z5: Error in Z.Z_Down(request).\n{e}")
            time.sleep(1)
        except Exception as e:
            print(f"Error in Z function \n {e}")
            #self.console_sig.emit(f"Error in Z function \n {e}")
            self.main.parent_connection.send(f"Error Z5: Error in Z.Z_Down().\n{e}")
            # self.printToConsole("Error in Dose function")

    def test_function(self, event):
        print("Hello, I am under the water, Please help me")
