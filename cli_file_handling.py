import collections
import json
# from Serial_file import Serial_Class               # Not a good idea becuase new connections will be formed and flow will be confusing, we can use main program instance itself
import threading


class Marking_Data:
    def __init__(self, main):
        try:
            self.main = main
            # self.file = file
            self._markData = collections.OrderedDict()
            self.previous_layer = None
            self.layer_height = None
            self.previous_line = ""
            self.previous_type = ""
            self.layer_height_helper_flag = False
            self.hatch_number = 1
            self.polyline_number = 1
            self.unit = 0
            self.total_layers = 0
            self.current_layer = 0
            self.point = 0
            self.layer_finished = False
            self.layer_key_list = []
            self.layer_key_index = 0
            self.line_key_list = []
            self.line_key_index = 0
        except Exception as e:
            self.main.parent_connection.send(f"Error C1: Error in cli_file_handline.__init__()\n{str(e)}")

    def get_file(self, file):
        try:
            self.file = file
        except Exception as e:
            self.main.parent_connection.send(f"Error C2: Error in cli_file_handline.get_file()\n{str(e)}")

    def checkForErrors(self):
        pass

    def generate_data(self):
        try:
            with open(self.file, "r") as file, open(r"/home/j2002/PycharmProjects/Branch1Patch1/Markingdata.txt",
                                                    "w") as file2:

                for line in file.readlines():
                    if line.startswith("$$LAYER/") and self.layer_height is None:
                        self.layer_height = float(line.split("/")[1])
                    elif line.startswith("$$DIMENSION/"):
                        temp_data = line.split("/")[1]
                        temp_data = temp_data.split(",")
                        x_lenght = float(temp_data[3]) - float(temp_data[0])
                        y_lenght = float(temp_data[4]) - float(temp_data[1])
                        z_lenght = float(temp_data[5]) - float(temp_data[2])
                        self.x_bit_factor = 67108863 // x_lenght        # To avoid decimal points
                        self.y_bit_factor = 67108863 // y_lenght
                        self.z_bit_factor = 67108863 // z_lenght

                    elif line.startswith("$$LAYER/") and self.layer_height_helper_flag == False:
                        self.layer_height = float(line.split("/")[1]) - self.layer_height
                        self.layer_height_helper_flag = True
                    if line.startswith("$$UNITS"):
                        self.unit = float(line.split("/")[1]) #* (10 ** (-3))       # dont multiply by 10^-3 becuase we need the coordinates in mm
                    elif line.startswith("$$LAYERS"):
                        self.total_layers = int(line.split("/")[1])
                    elif line.startswith("$$LAYER/"):
                        self.current_layer = float(line.split("/")[1])
                    elif line.startswith("$$HATCHES"):
                        line = line.split(",")
                        id = int(line[0].split("/")[1])
                        n = int(line[1])
                        total_coordinates = n * 4
                        if self.current_layer != self.previous_layer:
                            self.hatch_number = 1
                            self._markData[self.current_layer] = {"$$HATCHES 1": {
                                "id": id,
                                "n": n,
                                "total_coordinates": total_coordinates,
                                "coordinates": line[2:]
                            }
                            }
                            self.hatch_number = self.hatch_number + 1
                            self.previous_layer = self.current_layer
                            self.previous_type = "HATCHES"
                        elif self.current_layer == self.previous_layer:
                            key = f"$$HATCHES {self.hatch_number}"
                            self._markData[self.current_layer][key] = {
                                "id": id,
                                "n": n,
                                "total_coordinates": total_coordinates,
                                "coordinates": line[2:]
                            }
                            self.hatch_number = self.hatch_number + 1
                            self.previous_type = "HATCHES"

                    elif line.startswith("$$POLYLINE"):
                        line = line.split(",")
                        id = int(line[0].split("/")[1])
                        dir = int(line[1])
                        n = int(line[2])
                        if self.current_layer != self.previous_layer:
                            self.polyline_number = 1
                            self._markData[self.current_layer] = {"$$POLYLINE 1": {
                                "id": id,
                                "total_coordinates": n,
                                "dir": dir, "$$LAYER/"
                                            "coordinates": line[3:]
                            }
                            }
                            self.polyline_number = self.polyline_number + 1
                            self.previous_layer = self.current_layer
                            self.previous_type = "POLYLINE"
                        elif self.current_layer == self.previous_layer:
                            key = f"$$POLYLINE {self.polyline_number}"
                            self._markData[self.current_layer][key] = {
                                "id": id,
                                "total_coordinates": n,
                                "dir": dir,
                                "coordinates": line[3:]
                            }
                            self.polyline_number = self.polyline_number + 1
                            self.previous_type = "POLYLINE"

                    elif not line.startswith("$$"):                                    #if else is used $$HEADERSTART and $$GEOMETRYSTART will cause errors
                        line = line.split()                  #write logic for hatches or polylines occupying multiple lines
                        if self.previous_type == " POLYLINE":
                            key = f"$$POLYLINE {self.polyline_number}"
                            self._markData[self.current_layer][key]["coordinates"] = self._markData[self.current_layer][key]["coordinates"] + line
                        else:
                            key = f"$$HATCHES {self.hatch_number}"
                            self._markData[self.current_layer][key]["coordinates"] = self._markData[self.current_layer][key]["coordinates"] + line
                    else:
                        continue


                    self.previous_line = line


                json.dump(self._markData, file2, indent=4)
            for key in self._markData.keys():
                self.layer_key_list.append(key)              # A list of layers
                self._markData[key]["Total H/P"] = len(list(self._markData[key].keys()))
            # print(self.layer_key_list)

            self.main.file_data_display.setText(
                f"Layers: {self.total_layers} \nLayer thickness: {self.layer_height} \nUnits: {self.unit} \n\n\n")
            self.main.start_print.setEnabled(True)
            self.main.stop_print.setEnabled(True)


        except Exception as e:
            print(f"Generation of Marking Data failed with error {str(e)}")
            self.main.parent_connection.send(f"Error C3: Error in cli_file_handling.generate_data()\n{str(e)}")

    def initialise_print(self):
        try:
            self.main.start_print.setStyleSheet(self.main.current_style)
            #self.main.serial.serial_write(
             #   f"Layers: {self.total_layers} \nLayer thickness: {self.layer_height} \nUnits: {self.unit} \n\r")
            if self._markData is not None:
                self.scan_thread = threading.Thread(target=self.start_print_temp)
                self.scan_thread.daemon = True
                self.scan_thread.start()
            else:
                print("No data to start print")
                self.main.parent_connection.send("No data to start print")
        except Exception as e:
            self.main.parent_connection.send(f"Error C4: Error in cli_file_handline.initialise_print()\n{str(e)}")

    def start_printing_operation(self):
        try:
            self.payload = []
            coord = ""
            first_coordinate_in_layer = 1
            while coord != "finish":
                coord = self.get_next_pair()
                if isinstance(coord, list):
                    x_data = coord[0]
                    y_data = coord[1]
                    if x_data > 0 and y_data > 0:
                        if first_coordinate_in_layer == 1:
                            _command = self.main.scancard.make_command(x_data,y_data,0,"jump")
                            first_coordinate_in_layer = 0
                            continue
                        else:
                            _command = self.main.scancard.make_command(x_data,y_data,0,"mark")
                            if len(self.payload) <= 100:
                                self.payload.append(_command)
                            else:
                                resp = self.main.scancard.send_command(self.payload)
                                self.payload = []        # For now assuming 100 percent success rate
                                if resp:
                                    self.payload = []
                                else:
                                    pass                 # Type code to try to resend the commands in the failed transmissions
                                #self.main.scancard.close_connection()

                elif coord == "Layer complete":
                     self.main.scancard.send_command(b'd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') #Start output
                     resp = self.main.scancard.send_command(self.payload)


                elif coord == "Print complete":
                    coord = "finish"
                elif coord == "H/P complete":
                    print(coord)
                else:
                    #print(coord)
                    print("unknown response")
                    break



        except Exception as e:
            pass

    def start_print_temp(self):
        print("Debug 1")
        try:
            #Send initial data like total layers, layer height etc and also send the number of hatches/polylines in this it will make the logic easier to handle
            # self.point = 0                            # To start the operation at the beginning of the file always, not sure if neededd
            # self.layer_finished = False
            # self.layer_key_index = 0
            # self.line_key_index = 0


            #data = "OK\r\n"
            # self.main.serial.serial_write("Testing communication") #
            coord = self.get_next_pair()
            #print("coord", coord)
            to_send = f"X {coord[0]} Y {coord[1]}\r\n"
            self.main.serial.serial_write(to_send)
            while True:
                try:
                    if self.main.scanner_child_conn.poll(1):
                        data = self.main.scanner_child_conn.recv()
                        print(data)
                        if data == "finish":
                            print("Finished")
                            break
                        if "OK\r\n" in data:
                            print("in")
                            coord = self.get_next_pair()
                            print("coord", coord)
                            to_send = f"X {coord[0]} Y {coord[1]}\r\n"
                            if to_send is not None:
                                self.main.serial.serial_write(to_send)
                                print(to_send)
                    coord = self.get_next_pair()
                    print("coord", coord)
                    # else:
                    #     print(f"Garbage data received \n {data}")
                except Exception as e:
                    print(f"Generation of Marking Data failed with error {str(e)}")
                    self.main.parent_connection.send(f"Error C5: Error in cli_file_handling.start_print_temp()(Loop)\n{str(e)}")

        except Exception as e:
            self.main.parent_connection.send(f"Error C6: Error in cli_file_handling.start_print_temp()\n{str(e)}")

    # def start_print(self):
    #     self.main.serial.serial_write(
    #         f"Layers: {self.total_layers} \nLayer thickness: {self.layer_height} \nUnits: {self.unit} \n\r")
    #     if self.main.scanner_child_conn.recv() == "Ok start":
    #         while True:
    #             try:
    #                 if self.layer_key_index < len(self.layer_key_list):
    #                     self.layer_line_list = list(self._markData[self.layer_key_list[self.layer_key_index]].keys())
    #                     if self.line_key_index < len(self.layer_line_list):
    #                         coordinate = self._markData[self.layer_key_list[self.layer_key_index]][
    #                             self.layer_line_list[self.line_key_index]]["coordinates"]
    #                         n = self._markData[self.layer_key_list[0]][self.layer_line_list[0]]["total_coordinates"]
    #
    #                         if self.point < n:
    #                             x = coordinate[self.point]
    #                             y = coordinate[self.point + 1]
    #                             self.point = self.point + 2
    #                             return [x, y]
    #                         else:
    #                             print("Hatch or polyline complete")
    #                             self.line_key_index = self.line_key_index + 1
    #                             self.point = 0
    #
    #                     else:
    #                         print("Layer finsihed")
    #                         self.layer_key_index = self.layer_key_index + 1
    #                         self.line_key_index = 0
    #                 else:
    #                     print("Print finished")
    #             except Exception as e:
    #                 print(f"Failed to get the next coordinnates due to the following error \n {e}")

    def get_next_pair(self):
        try:
            if self.layer_key_index < len(self.layer_key_list):
                self.layer_line_list = list(self._markData[self.layer_key_list[self.layer_key_index]].keys())  #Will get a list of all the layers
                if self.line_key_index < len(self.layer_line_list):
                    coordinate = self._markData[self.layer_key_list[self.layer_key_index]][
                        self.layer_line_list[self.line_key_index]]["coordinates"]
                    #n = self._markData[self.layer_key_list[0]][self.layer_line_list[0]]["total_coordinates"]          #can't figure out why i had given zero index initiallly, maybe as a trial
                    n = self._markData[self.layer_key_list[self.layer_key_index]][self.layer_line_list[self.line_key_index]]["total_coordinates"]   #n gives total number of points i.e x and y separated and added
                    if self.point < n:
                        x = float(coordinate[self.point]) * self.unit
                        y = float(coordinate[self.point + 1]) * self.unit
                        self.point = self.point + 2
                        return [x, y]
                    else:
                        print("Hatch or polyline complete")
                        self.main.parent_connection.send("Hatch or polyline complete")
                        self.line_key_index = self.line_key_index + 1
                        #self.main.serial.serial_write(f"hatches/polylines {self._markData[self.layer_key_index]['Total H/p']}")   # sending the number of hatches/polylines in the next layer
                        self.point = 0
                        return "H/P complete"

                else:
                    print("Layer finsihed")
                    self.main.parent_connection.send("Layer finsihed")
                    self.layer_key_index = self.layer_key_index + 1
                    self.line_key_index = 0
                    return "Layer complete"
            else:
                print("Print finished")
                self.main.parent_connection.send("Print finsihed")
                return "Print complete"
        except Exception as e:
            print(f"Failed to get the next coordinnates due to the following error \n {str(e)}")
            self.main.parent_connection.send(f"Error C7: Error in cli_file_handling.get_next_pair()\n{str(e)}")

            # if layer == "first":
            #     self.mark_layer = self._markData[self.layer_key_list[0]]
            #     for key in self.mark_layer.keys():
            #         self.line_key_list.append(key)
            # if not self.layer_finished:
            #     if
            #     n = self._markData[self.layer_key_index][self.line_key_index]["n"]
            #     if self.point < n:
            #


# def main():
#     print("Hello")
#     file = r"/home/j2002/Desktop/cli_file_set/IISC logo.cli"
#     obj = Marking_Data("main")
#     obj.get_file(file)
#     obj.generate_data()
#     # for i in range(60):
#     #     coord = obj.get_next_pair()
#     #     print(coord)
#     #print(obj._markData)
#     # di = obj._markData
#     # for key in di.keys():
#     #     temp = di[key]
#     #     for key1 in temp.keys():
#     #         if key1 == "Total H/P":
#     #             print(temp[key1])
#
#
#
#
# if __name__ == "__main__":
#     main()
