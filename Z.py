import requests
import time


class Zmotion:
    def __init__(self):
        pass

    def Zaxis_up(self, object):
        pass

    def Zaxis_down(self, object):
        pass

    def Z_Up(self):
        try:
            move_z = {
                "command": "move_Z10"
            }
            try:
                print("Moving z")
                req = requests.post(url=f"http://{self.api}/api/printer/command", params=self.params,
                                    json=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Move Z Request timed out. Connection could not be established.")
                # self.printToConsole("Hopper Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"A Z request error occurred: {e}")
                # self.printToConsole(f"An Hopper request error occurred: {e}"
            time.sleep(5)
        except:
            print("Z_UP error")

    def set_distance(self, button):
        pass

    def Z_Down(self):
        try:
            move_z = {
                "command": "move_Z10"
            }
            try:
                print("Moving z")
                req = requests.post(url=f"http://{self.api}/api/printer/command", params=self.params,
                                    json=move_z, timeout=5)
                req.raise_for_status()
            except requests.exceptions.Timeout:
                print("Move Z Request timed out. Connection could not be established.")
                # self.printToConsole("Hopper Request timed out. Connection could not be established.")
            except requests.exceptions.RequestException as e:
                print(f"A Z request error occurred: {e}")
                # self.printToConsole(f"An Hopper request error occurred: {e}"
            time.sleep(5)
        except:
            print("Z_UP error")
