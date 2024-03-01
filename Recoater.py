import time

class Recoater:
    def __init__(self,parent):
        self.parent = parent
    def Home_recoater(self):  # Function to home the recoater system
        self.home.setStyleSheet(self.current_style)
        if self.debug_var == 2:
            self.printToConsole("Homing recoater system")
        try:
            cmd = "Recoater_RV\r"
            if self.debug_var == 2:
                self.printToConsole(f"Command:{cmd}")
                print(f"Command:{cmd}")
            self.serial.serial_write(cmd)
        except Exception as e:
            print("Homing error \n {e}")
            self.printToConsole("Recoater Homing error")

    def recoater_emergency(self):  # Function to handing the emergency stoppage of the recoater system
        print("Emergency recoater stop initiated")
        self.printToConsole("Emergency recoater stop initiated")
        self.recoater_Estop.setStyleSheet(self.current_style)
        try:
            cmd = "Recoater_STOP_IN\r"
            self.serial.serial_write(cmd)

            time.sleep(1)

            cmd = "Roller_STOP_IN\r"
            self.serial.serial_write(cmd)
        except Exception as e:
            print("Recoater emergerncy stop errror \n {e}")
            self.printToConsole("Recoater emergency stop error")

    def RPM(self, rpm, num, auto="0"):  # Function to set the RPM to the motors in the recoater system
        try:
            global RECOATER_RPM
            global ROLLER_RPM
            if rpm == True and num == 0:  # When RPM is set using line edit widget, i.e entering the value for MOTOR 1
                val = self.recoaterRPM.text()
                if val.isdigit():
                    val = int(val)
                    RECOATER_RPM = val
                    print(f"new recoater rpm: {RECOATER_RPM}")
                    if auto != "auto":
                        self.parent_connection.send(f"new recoater rpm: {RECOATER_RPM}")
                    if val < 40 or val > 3150:
                        print("Please enter valid inputs")
                        if auto != "auto":
                            self.parent_connection.send("Please enter valid inputs")
                    else:
                        if self.serial.serial.is_open:
                            cmd = "Recoater_RPM" + f" {RECOATER_RPM}\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                        else:
                            print("Serial port is not open")
                            if auto != "auto":
                                self.parent_connection.send("Serial port is not open")

                else:
                    print("Please enter valid inputs")
                    if auto != "auto":
                        self.parent_connection.send("Please enter valid inputs")
            elif rpm == False and num == 0:  # Setting rpm for motor 2 by direct entry
                val = self.rollerRPM.text()
                if val.isdigit():
                    val = int(val)
                    ROLLER_RPM = val
                    print(f"new roller rpm: {ROLLER_RPM}")
                    if val < 40 or val > 3150:
                        print("Please enter valid inputs")
                        if auto != "auto":
                            self.parent_connection.send("Please enter valid inputs")
                    else:
                        if self.serial.serial.is_open:
                            cmd = "Roller_RPM" + f" {ROLLER_RPM}\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.parent_connection.send(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                        else:
                            print("Serial port is not open")
                            if auto != "auto":
                                self.parent_connection.send("Serial port is not open")

                else:
                    print("Please enter valid inputs")
                    if auto != "auto":
                        self.parent_connection.send("Please enter valid inputs")
            elif rpm == True and num != 0:  # Changing RPM of motor 1 by clicking one of the given buttons
                if num == 5:
                    self.R5.setStyleSheet(self.current_style)
                elif num == 10:
                    self.R10.setStyleSheet(self.current_style)
                elif num == 100:
                    self.R100.setStyleSheet(self.current_style)
                elif num == -5:
                    self.mR5.setStyleSheet(self.current_style)
                elif num == -10:
                    self.mR10.setStyleSheet(self.current_style)
                elif num == -100:
                    self.mR100.setStyleSheet(self.current_style)
                RECOATER_RPM = RECOATER_RPM + num
                if self.serial.serial.is_open:
                    cmd = "Recoater_RPM" + f" {RECOATER_RPM}\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        if auto != "auto":
                            self.parent_connection.send(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    self.parent_connection.send("Serial port is not open")

            else:  # Changing the RPM of motor 2 by clicking one the given buttons
                if num == 5:
                    self.RO5.setStyleSheet(self.current_style)
                elif num == 10:
                    self.RO10.setStyleSheet(self.current_style)
                elif num == 100:
                    self.RO100.setStyleSheet(self.current_style)
                elif num == -5:
                    self.mRO5.setStyleSheet(self.current_style)
                elif num == -10:
                    self.mRO10.setStyleSheet(self.current_style)
                elif num == -100:
                    self.mRO100.setStyleSheet(self.current_style)
                ROLLER_RPM = ROLLER_RPM + num
                if self.serial.serial.is_open:
                    cmd = "Roller_RPM" + f" {ROLLER_RPM}\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        if auto != "auto":
                            self.parent_connection.send(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    if auto != "auto":
                        self.parent_connection.send("Serial port is not open")
        except Exception as e:
            print(f"RPM error \n {e}")
            if auto != "auto":
                self.parent_connection.send("Error")
            if self.debug_var == 2:
                print("Trying to open new serial port")
                if auto != "auto":
                    self.parent_connection.send("Trying to open new serial port")
                try:
                    self.serial.connect()
                except:
                    print("unable to establish serial communication")
                    if auto != "auto":
                        self.parent_connection.send("Trying to open new serial port")

    def start(self, motor_select):  # Function to handle the start of the motors
        try:
            if motor_select:  # Motor 1
                self.recoater.setStyleSheet(
                    self.current_style)  # this type of line in all functions is used for the click effect
                if self.serial.serial.is_open:
                    cmd = "Recoater_START\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        print("Debug statement")
                        self.printToConsole(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    self.printToConsole("Serial port is not open")

            else:  # Motor 2
                self.roller.setStyleSheet(self.current_style)
                if self.serial.serial.is_open:
                    cmd = "Roller_START\r"
                    print(f"Command:{cmd}")
                    if self.debug_var == 2:
                        self.parent_connection.send(f"Command:{cmd}")
                    self.serial.serial_write(cmd)
                else:
                    print("Serial port is not open")
                    self.parent_connection.send("Serial port is not open")

        except Exception as e:
            print(f"start function Error\n {e}")
            self.parent_connection.send("Error")
            print("Trying to open new serial port")
            self.parent_connection.send("Trying to open new serial port")
            try:
                self.serial.open()
            except Exception as e:
                print(f"unable to establish serial communication due to \n {e}")
                self.printToConsole("unable to establish serial communication")

    def Brake(self, motor_select):  # Function to handle the breaking of recoater motors
        if motor_select:
            self.brake.setStyleSheet(self.current_style)
        else:
            self.Rbrake.setStyleSheet(self.current_style)

        try:
            if self.serial.serial.is_open:
                if motor_select:
                    self.brake.setStyleSheet(self.current_style)
                    try:
                        cmd = "Recoater_BRAKE\r"
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except:
                        print("Error in braking Motor 1")
                        self.printToConsole("Error in braking Motor 1")
                else:
                    self.Rbrake.setStyleSheet(self.current_style)  # R prefix indicated motor 2 / ROLLER
                    try:
                        cmd = "Roller_BRAKE\r"
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except:
                        print("Error in braking R Motor")
                        self.printToConsole("Error in braking R Motor")

            else:
                print("Unable to detect a serial connection")
                self.printToConsole("Unable to detect a serial connection")

        except Exception as e:
            print("Error in brake function \n {e}")
            self.printToConsole("Error in brake function")

    def instantStop(self,
                    motor_select):  # Function to instantaneously stop the motor, the buttons are not displayed in the GUI
        try:
            if self.serial.serial.is_open:
                if motor_select:
                    try:
                        cmd = "Recoater_STOP_IN\r"
                        print(f"Command:{cmd}")
                        if self.debug_var == 2:
                            self.printToConsole(f"COMMAND:{cmd}")
                        self.serial.serial_write(cmd)

                    except Exception as e:
                        print(f"Error in INSTANTANEOUSLY braking Motor 1 \n {e}")
                        self.printToConsole("Error in INSTANTANEOUSLY braking Motor 1")
                else:
                    try:
                        cmd = "Roller_STOP_IN\r"
                        print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in INSTANTANEOUSLY braking R Motor\n{e}")
                        self.printToConsole("Error in INSTANTANEOUSLY braking R Motor")

            else:
                print("Unable to detect a serial connection")
                self.printToConsole("Unable to detect a serial connection")

        except:
            print("Error in instant brake function")
            self.printToConsole("Error in instant brake function")

    def deceleratingStop(self, motor_select):  # To stop the motors without a jerk
        if motor_select:
            self.decStop.setStyleSheet(self.current_style)
        else:
            self.RdecStop.setStyleSheet(self.current_style)
        try:
            if self.serial.serial.is_open:
                if motor_select:
                    self.decStop.setStyleSheet(self.current_style)
                    try:
                        cmd = "Recoater_STOP_DC\r"
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                            print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in DECELERATING brakes in Motor 1\n{e}")
                        self.printToConsole("Error in DECELERATING brakes in Motor 1")
                else:
                    self.RdecStop.setStyleSheet(self.current_style)
                    try:
                        cmd = "Roller_STOP_DC\r"
                        if self.debug_var == 2:
                            self.printToConsole(f"Command:{cmd}")
                            print(f"Command:{cmd}")
                        self.serial.serial_write(cmd)
                    except Exception as e:
                        print(f"Error in DECELERATING brakes in R Motor\n{e}")
                        self.printToConsole("Error in DECELERATING brakes in R Motor")

            else:
                print("Unable to detect a serial connection")
                self.printToConsole("Unable to detect a serial connection")

        except Exception as e:
            print(f"Error in decelerating brake function\n{e}")
            self.printToConsole("Error in decelerating brake function")

    def changeDirection(self, motor_select,
                        auto="0"):  # Function to handle the change of direction of motion of recoater motors
        if motor_select:
            self.changeDIR.setStyleSheet(self.current_style)
        else:
            self.RchangeDIR.setStyleSheet(self.current_style)

        try:
            global MOTOR_DIR
            global RMOTOR_DIR
            if self.serial.serial.is_open:
                if motor_select:
                    self.changeDIR.setStyleSheet(self.current_style)
                    try:
                        if MOTOR_DIR:  # Variable to store the direction of motion
                            cmd = "Recoater_Go_Left\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            MOTOR_DIR = False
                            if auto != "auto":
                                self.changeDIR.setText("Move Right")
                        else:
                            cmd = "Recoater_Go_Right\r"
                            self.serial.serial_write(cmd)
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            MOTOR_DIR = True
                            if auto != "auto":
                                self.changeDIR.setText("Move left")
                    except Exception as e:
                        print(f"Error in changing direction of roation of Motor 1\n{e}")
                        if auto != "auto":
                            self.printToConsole("Error in changing direction of roation of Motor 1")

                else:
                    self.RchangeDIR.setStyleSheet(self.current_style)
                    try:
                        if RMOTOR_DIR:
                            cmd = "Roller_RV\r"
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")

                            print(f"command:{cmd}")
                            self.serial.serial_write(cmd)
                            RMOTOR_DIR = False
                            if auto != "auto":
                                self.RchangeDIR.setText("AntiClockwise")
                        else:
                            cmd = "Roller_FW\r"
                            print(f"Command:{cmd}")
                            if self.debug_var == 2:
                                if auto != "auto":
                                    self.printToConsole(f"Command:{cmd}")
                                print(f"Command:{cmd}")
                            self.serial.serial_write(cmd)
                            RMOTOR_DIR = True
                            if auto != "auto":
                                self.RchangeDIR.setText("Clockwise")
                    except Exception as e:
                        print(f"Error in changing direction of roation of Motor 2\n{e}")
                        if auto != "auto":
                            self.printToConsole("Error in changing direction of rotation of Motor 2")
            else:
                print("Serial port not open")
                if auto != "auto":
                    self.printToConsole("Serial port not open")

        except Exception as e:
            print("Error in the direction changing function\n{e}")
            if auto != "auto":
                self.printToConsole("Error in the direction changing function")

    def test_function(self, event):
        print("Hello Recoater, I am under the water, Please help me")
