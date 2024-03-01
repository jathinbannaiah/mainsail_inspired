import serial as sr
import serial.tools.list_ports
import platform
import requests
import time
#COMMANDS
#                    "Roller_FW",
#                    "Roller_RV",
#                    "Roller_STOP_IN",
#                    "Roller_STOP_DC",
#                    "Roller_START",
#                    "Roller_RUN_FW",
#                    "Roller_RUN_RV",
#                    "Roller_BRAKE",
#                    "Roller_RPM",
#                    "Recoater_FW",
#                    "Recoater_RV",
#                    "Recoater_STOP_IN",
#                    "Recoater_STOP_DC",
#                    "Recoater_START",
#                    "Recoater_RUN_FW",
#                    "Recoater_RUN_RV",
#                    "Recoater_BRAKE",
#                    "Recoater_Go_Left",
#                    "Recoater_Go_Right",
#                    "Recoater_RPM"
def testing_p(main):

    z_var = 0.1
    main.test.setStyleSheet(main.current_style)
    api = "172.19.253.103:7125"               #write the api port
    #
    n = 0
    command = "Roller_RPM 312\r"  # Don't forget carriage return at the end of of the command
    main.serial.serial_write(command)

    while n < 1000:
        # if main.serial.serial.is_open:
        #     hopper_cmd = {
        #                          "script": "move_hopper_left"
        #                     }
        #     try:
        #         print("Opening Hopper")
        #         req = requests.post(url=f"http://{api}/printer/gcode/script",
        #         params=hopper_cmd, timeout=2)
        #     except requests.exceptions.Timeout as e:
        #         print(f"Error M15: Hopper Request timed out. Connection could not be established.\n{e}")
        #
        #     except requests.exceptions.RequestException as e:
        #         print(f"Error M16: An Hopper request error occurred: {e}")

            time.sleep(1)

            command = "Roller_RUN_RV\r"  # Don't forget carriage return at the end of of the command
            main.serial.serial_write(command)

            time.sleep(1)
            print("FW")
            command = "Recoater_RUN_FW\r"              #Don't forget carriage return at the end of of the command
            main.serial.serial_write(command)
            time.sleep(8)

            # move_z = {
            #     "script": f"G1 Z{z_var}"
            # }
            # print(z_var)
            # try:
            #     req = requests.post(url=f"http://{api}/printer/gcode/script",
            #                         params=move_z, timeout=2)
            #     req.raise_for_status()
            #     z_var = z_var + 0.1
            # except requests.exceptions.Timeout as e:
            #     print(f"Error M17: Move Z Request timed out. Connection could not be established.")
            #
            # except requests.exceptions.RequestException as e:
            #     print(f"Error M18: A Z request error occurred: {e}")
            #



            # hopper_cmd = {
            #     "script": "move_hopper_right"
            # }
            # try:
            #     print("Opening Hopper")
            #     req = requests.post(url=f"http://{api}/printer/gcode/script",
            #                         params=hopper_cmd, timeout=2)
            # except requests.exceptions.Timeout as e:
            #     print(f"Error M15: Hopper Request timed out. Connection could not be established.\n{e}")
            #
            # except requests.exceptions.RequestException as e:
            #     print(f"Error M16: An Hopper request error occurred: {e}")
            #
            # time.sleep(1)
            #
            # command = "Roller_RUN_FW\r"  # Don't forget carriage return at the end of of the command
            # main.serial.serial_write(command)
            #
            # time.sleep(1)

            command = "Recoater_RUN_RV\r"  # Don't forget carriage return at the end of of the command
            main.serial.serial_write(command)
            time.sleep(8)
            #
            # move_z = {
            #     "script": f"G1 Z{z_var}"
            # }
            # print(z_var)
            # try:
            #
            #     req = requests.post(url=f"http://{api}/printer/gcode/script",
            #                         params=move_z, timeout=2)
            #     req.raise_for_status()
            #     z_var = z_var + 0.1
            # except requests.exceptions.Timeout as e:
            #     print(f"Error M17: Move Z Request timed out. Connection could not be established.")
            #
            # except requests.exceptions.RequestException as e:
            #     print(f"Error M18: A Z request error occurred: {e}")

            n = n + 1







    # #HOPPER
#         hopper_cmd = {
#                 "script": "move_hopper_right"
#             }
#         try:
#             print("Opening Hopper")
#             req = requests.post(url=f"http://{api}/printer/gcode/script",
#                                 params=hopper_cmd, timeout=2)
#         except requests.exceptions.Timeout as e:
#             print(f"Error M15: Hopper Request timed out. Connection could not be established.\n{e}")
#
#         except requests.exceptions.RequestException as e:
#             print(f"Error M16: An Hopper request error occurred: {e}")



#Z
        #  move_z = {
        #             "script": ""
        #         }
        # try:
        #     req = requests.post(url=f"http://{api}/printer/gcode/script",
        #                         params=move_z, timeout=2)
        #     req.raise_for_status()
        # except requests.exceptions.Timeout as e:
        #     print(f"Error M17: Move Z Request timed out. Connection could not be established.")
        #
        # except requests.exceptions.RequestException as e:
        #     print(f"Error M18: A Z request error occurred: {e}")
#
#



