import sys
from PyQt5.QtCore import QTimer, QTime, Qt
import time

class Time():
    def __init__(self,parent):
        try:
            self.parent = parent
            self.timer = QTimer()
            self.time = QTime(0, 0, 0)
        except Exception as e:
            self.parent.parent_connection.send(f"Error T0: Error in timing.__init__()\n{e}")

    def stopTimer(self):
        try:
            if self.parent.debug_var == 2:
                print("stop timer")
                self.parent.parent_connection.send("Stoping Timer")
            self.timer.stop()
            #Disconnect existing timeout signal connections, if any
            self.timer.timeout.disconnect()
        except Exception as e:
            print(f"stop timer error: {e}")
            self.parent.parent_connection.send(f"Error T1: Error in timing.stopTimer()\n{e}")

    def resetTimer(self):
        try:
            self.parent.time_elapsed.setText("   00:00:00")
            self.time.setHMS(0, 0, 0)
            self.time = QTime(0, 0, 0)
            self.timer.stop()
            #Disconnect existing timeout signal connections, if any
            self.timer.timeout.disconnect()
        except Exception as e:
            print(f"reset timer error: {e}")
            self.parent.parent_connection.send(f"Error T2: Error in timing.resetTimer()\n{e}")


    def updateTime(self):
        try:
            self.time = self.time.addSecs(1)  # Add 1 second to elapsed time
            time_str = self.time.toString("   hh:mm:ss")
            self.parent.time_elapsed.setText(time_str)
        except Exception as e:
            print(f"update timer error: {e}")
            self.parent.parent_connection.send(f"Error T3: Error in timing.updateTimer()\n{e}")

    def resumeTimer(self):
        try:
            self.timer.timeout.connect(self.updateTime)
            self.timer.start(1000)  # Update time every 1 second
        except Exception as e:
            print(f"resume timer error: {e}")
            self.parent.parent_connection.send(f"Error T4: Error in timing.resu,eTimer()\n{e}")


    def startTimer(self):
        try:
            self.time.start()
            self.time.setHMS(0, 0, 0)
            self.timer.timeout.connect(self.updateTime)
            self.timer.start(1000)  # Update time every 1 second
        except Exception as e:
            print(f"start timer error: {e}")
            self.parent.parent_connection.send(f"Error T5: Error in timing.startTimer()\n{e}")

