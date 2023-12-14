import collections
import json


class Marking_Data:
    def __init__(self, main, file):
        self.main = main
        self.file = file
        self._markData = collections.OrderedDict()
        self.previous_layer = None
        self.layer_height = None
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

    def checkForErrors(self):
        pass

    def generate_data(self):
        try:
            with open(self.file,"r") as file,open(r"/home/j2002/PycharmProjects/Branch1Patch1/Markingdata.txt", "w") as file2:

                for line in file.readlines():
                    if line.startswith("$$LAYER/") and self.layer_height is None:
                        self.layer_height = float(line.split("/")[1])
                    elif line.startswith("$$LAYER/") and self.layer_height_helper_flag == False:
                        self.layer_height = float(line.split("/")[1]) - self.layer_height
                        self.layer_height_helper_flag = True
                    if line.startswith("$$UNITS"):
                        self.unit = float(line.split("/")[1]) * (10**(-3))
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
                            self._markData[self.current_layer] = {"$$HATCHES 1":{
                                "id": id,
                                "n": n,
                                "total_coordinates": total_coordinates,
                                "coordinates": line[2:]
                            }
                            }
                            self.hatch_number = self.hatch_number + 1
                            self.previous_layer = self.current_layer
                        elif self.current_layer == self.previous_layer:
                            key = f"$$HATCHES {self.hatch_number}"
                            self._markData[self.current_layer][key] = {
                                "id": id,
                                "n": n,
                                "total_coordinates": total_coordinates,
                                "coordinates": line[2:]
                            }
                            self.hatch_number = self.hatch_number + 1

                    elif line.startswith("$$POLYLINE"):
                        line = line.split(",")
                        id = int(line[0].split("/")[1])
                        dir = int(line[1])
                        n = int(line[2])
                        if self.current_layer != self.previous_layer:
                            self._markData[self.current_layer] = {"$$POLYLINE 1":{
                                "id": id,
                                "total_coordinates": n,
                                "dir": dir,"$$LAYER/"
                                "coordinates": line[3:]
                            }
                            }
                            self.hatch_number = self.hatch_number + 1
                            self.previous_layer = self.current_layer
                        elif self.current_layer == self.previous_layer:
                            key = f"$$POLYLINE {self.hatch_number}"
                            self._markData[self.current_layer][key] = {
                                "id": id,
                                "total_coordinates": n,
                                "dir": dir,
                                "coordinates": line[3:]
                            }
                            self.hatch_number = self.hatch_number + 1

                json.dump(self._markData,file2,indent = 4)
            for key in self._markData.keys():
                self.layer_key_list.append(key)
            #print(self.layer_key_list)

        except Exception as e:
            print(f"Generation of Marking Data failed with error {e}")



    def get_next_pair(self):
        try:
            if self.layer_key_index < len(self.layer_key_list):
                self.layer_line_list = list(self._markData[self.layer_key_list[self.layer_key_index]].keys())
                if self.line_key_index < len(self.layer_line_list):
                    coordinate = self._markData[self.layer_key_list[self.layer_key_index]][self.layer_line_list[self.line_key_index]]["coordinates"]
                    n = self._markData[self.layer_key_list[0]][self.layer_line_list[0]]["total_coordinates"]

                    if self.point < n:
                        x =coordinate[self.point]
                        y = coordinate[self.point + 1]
                        self.point = self.point + 2
                        return [x,y]
                    else:
                        print("Hatch or polyline complete")
                        self.line_key_index = self.line_key_index + 1
                        self.point = 0

                else:
                    print("Layer finsihed")
                    self.layer_key_index = self.layer_key_index + 1
                    self.line_key_index = 0
            else:
                print("Print finished")
        except Exception as e:
            print(f"Failed to get the next coordinnates due to the following error \n {e}")


            # if layer == "first":
            #     self.mark_layer = self._markData[self.layer_key_list[0]]
            #     for key in self.mark_layer.keys():
            #         self.line_key_list.append(key)
            # if not self.layer_finished:
            #     if
            #     n = self._markData[self.layer_key_index][self.line_key_index]["n"]
            #     if self.point < n:
            #










#
# def main():
#     print("Hello")
#     file = r"/home/j2002/Desktop/cli_file_set/IISC logo.cli"
#     obj = Marking_Data("main", file)
#     obj.generate_data()
#     for i in range(60):
#         coord = obj.get_next_pair()
#         print(coord)
#     #print(obj._markData)
#
#
#
# if __name__ == "__main__":
#     main()

