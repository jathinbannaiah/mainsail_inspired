import sys
from PyQt5.QtCore import QTimer, QTime, Qt
import time

class Time():
    def __init__(self,parent):
        self.parent = parent
        self.timer = QTimer()
        self.time = QTime(0, 0, 0)

    def stopTimer(self):
        print("stop timer")
        self.timer.stop()
        #Disconnect existing timeout signal connections, if any
        self.timer.timeout.disconnect()

    def resetTimer(self):
        self.parent.time_elapsed.setText("   00:00:00")
        self.time.setHMS(0, 0, 0)
        self.time = QTime(0, 0, 0)
        self.timer.stop()
        #Disconnect existing timeout signal connections, if any
        self.timer.timeout.disconnect()


    def updateTime(self):
        self.time = self.time.addSecs(1)  # Add 1 second to elapsed time
        time_str = self.time.toString("   hh:mm:ss")
        self.parent.time_elapsed.setText(time_str)

    def resumeTimer(self):
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)  # Update time every 1 second


    def startTimer(self):
        self.time.start()
        self.time.setHMS(0, 0, 0)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)  # Update time every 1 second

