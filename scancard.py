import socket
import struct
import sys
import time
from cube_commands_hatch import *
from cube_commands_boundary import *

class ScanCard():
    def __init__(self):
        #Try not to import main instance in this file
        self.ip = "10.196.22.75"
        self.passw = ""
        self.port = 23
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # opens the connection

        self.client_socket.connect((self.ip, self.port))
        print(self.receive_response())

    def halt_marking(self):
        self.client_socket.send(b'd\x07\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print("response:",self.receive_response())

    def stop_marking(self):
        self.client_socket.send(b'd\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print("response:",self.receive_response())

    def continue_marking(self):
        self.client_socket.send(b'd\x07\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print("response:",self.receive_response())


    def draw_square2_(self):
        count = 0
        to_send = []
        index_tracker = 0
        for item in cube_commands_outline:
            if (index_tracker + 90) > (len(cube_commands_outline) - 1):
                #print("Test2)")
                to_send = cube_commands_outline[index_tracker:]
                payload = b''.join(to_send)
                self.client_socket.send(payload)
                print("response:",self.receive_response())
                break
            else:
                if count < 90:
                    to_send.append(item)
                    count += 1
                    continue
                elif count == 90:
                    #print("test1")
                    payload = b''.join(to_send)
                    self.client_socket.send(payload)
                    print("response:",self.receive_response())
                    count = 0
                    to_send = []
                    index_tracker += 90
                    time.sleep(1)
                else:
                    print("help")

    def hatch_square2_(self):
        count = 0
        to_send = []
        index_tracker = 0
        for item in cude_commands_fill:
            if (index_tracker + 90) > (len(cude_commands_fill) - 1):
                print("test2")
                to_send = cude_commands_fill[index_tracker:]
                payload = b''.join(to_send)
                self.client_socket.send(payload)
                print("response:",self.receive_response())
                break
            else:
                if count < 90:
                    to_send.append(item)
                    count += 1
                    continue
                elif count == 90:
                    print("test1")
                    payload = b''.join(to_send)
                    self.client_socket.send(payload)
                    print("response:",self.receive_response())
                    count = 0
                    to_send = []
                    index_tracker += 90
                else:
                    print("help")
            index_tracker += 1
    def draw_square_(self):
        print("testS1")
        commands_ = [b'd\x01\xff\xff\xff\x02\xff\xff\xff\x02\x90_\x01\x00',
                     b'd\x01\xff\xff\xff\x02\xff\xff\xff\x00\x90_\x01\x00',
                     b'd\x01\xff\xff\xff\x00\xff\xff\xff\x00\x90_\x01\x00',
                     b'd\x01\xff\xff\xff\x00\xff\xff\xff\x02\x90_\x01\x00',
                     b'd\x01\xff\xff\xff\x02\xff\xff\xff\x02\x90_\x01\x00',
                     b'd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']
        payload = b''.join(commands_)
        self.client_socket.send(payload)
        print("response:",self.receive_response())
        #time.sleep(1)
        #self.close_connection()

    def change_speed(self,markS = 200000,jumpS = 200000):
        print(markS,jumpS)
        jump = struct.pack('<I', markS)
        mark = struct.pack('<I', jumpS)
        unused = struct.pack('<I', 0)
        command = b'd' + bytes([0x04]) + jump + mark + unused
        self.client_socket.send(command)
        print("response:",self.receive_response())

    def draw_triangle_(self):
        print("testT1")
        commands_ = [b'd\x01\xfe\xff\xff\x01\xff\xff\xff\x02\x90_\x01\x00',
                     b'd\x01\xff\xff\xff\x02\xff\xff\xff\x00\x90_\x01\x00',
                     b'd\x01\xff\xff\xff\x00\xff\xff\xff\x00\x90_\x01\x00',
                     b'd\x01\xfe\xff\xff\x01\xff\xff\xff\x02\x90_\x01\x00',
                     b'd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00']
        payload = b''.join(commands_)
        self.client_socket.send(payload)
        print("response:",self.receive_response())
        time.sleep(10)
        #self.close_connection()

    def send_command(self,usr_cmd = ""):
        #1460 bytes maximum size per packet
        #14 bytes command size
        # self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)   #opens the connection
        #
        # self.client_socket.connect((self.ip,self.port))
        # print(self.receive_response())

        command_identifier = 0x00   #0x02 start output command,led blink frequency increases

        # # 32-bit little-endian values
        AAAA = 0
        BBBB = 0   #In ascii 0x0A represents newline
        EEEE = 100000

        # Convert integers to little-endian byte representation
        AAAA_bytes = struct.pack('<I', AAAA)
        BBBB_bytes = struct.pack('<I', BBBB)
        EEEE_bytes = struct.pack('<I', EEEE)


        # commands = [b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00',
        #             b'd\x00\xfe\xff\xff\x01\xfe\xff\xff\x01\xa0\x86\x01\x00',
        #             b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        #             b'd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        #
        # ]

        #payload =b''.join(commands)


        # Concatenate the command
        command = b"d" + bytes([command_identifier]) + AAAA_bytes + BBBB_bytes + EEEE_bytes # Seems to e corrct but the response generated is not "exactly" in the required format

        #command = "cvers\r"            #carriage return is necessary
        #self.client_socket.send(command.encode('utf-8'))
        if usr_cmd != "":
            self.client_socket.send(usr_cmd)
            print("response:",self.receive_response())

        #self.client_socket.send(command)
        #self.client_socket.send(payload)
        # self.client_socket.send(b'd\x00\xfd\xff\xff\x03\xfd\xff\xff\x03\xa0\x86\x01\x00')
        self.client_socket.send(b'd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        #self.client_socket.send(b'd\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        #self.client_socket.send(b"d\x04\x10'\x00\x00\x10'\x00\x00\x00\x00\x00\x00")

        print("response:",self.receive_response())   #returns in ascii, of 0x64 corresponds to "d" character dont get confused with d in "hexadecimal"
        #print("response:",self.receive_response())                  #we need it
        #self.close_connection()

    def close_connection(self):
        self.client_socket.close()

    def receive_response(self):
        response = self.client_socket.recv(1024)
        return response
        #return response.decode('utf-8')


    def make_command(self,x,y,z, cmd_type):
        AAAA_bytes = struct.pack('<I', x)
        BBBB_bytes = struct.pack('<I', y)
        EEEE_bytes = struct.pack('<I', z)


        # Convert integers to little-endian byte representation
        # hexa_x = struct.pack('<I', hexa_x)
        # hexa_y = struct.pack('<I', hexa_y)
        # hexa_z = struct.pack('<I', hexa_z)

        # Concatenate the command
        #command = b"d" + bytes([command_identifier]) + hexa_x + hexa_y + hexa_z
        #print("command", command)

        if cmd_type == "mark":
            command_identifier = 0x01
            command = b'd' + bytes([command_identifier]) + AAAA_bytes + BBBB_bytes + EEEE_bytes
            print(command)

        elif cmd_type == "jump":
            command_identifier = 0x00
            command = b'd' + bytes([command_identifier]) + AAAA_bytes + BBBB_bytes + EEEE_bytes
            print(command)

        elif cmd_type == "start_output":
            command_identifier = 0x02
            command = b'd' + bytes([command_identifier]) + AAAA_bytes + BBBB_bytes + EEEE_bytes


        print("command", command,len(command))
        return command

        #If first coordinate in a layer then jump command or else mark command



    def check_if_CLIfile_loaded(self):
        pass


obj = ScanCard()
#obj.draw_triangle_()
#obj.draw_square2_()
#obj.hatch_square2_()
#obj.send_command()
#time.sleep(2)
# for i in range(50):
#     obj.draw_square_()
#     time.sleep(10)
#     obj.draw_triangle_()
#     time.sleep(10)
#print(obj.make_command(200000,200000,0000,'jump'))
print(obj.make_command(2,0,90000,'jump'))
# print(obj.make_command(16777215,16777215,90000,'jump'))
# print(obj.make_command(16777215,50331647,90000,'jump'))
# print(obj.make_command(33554430,50331647,90000,'jump'))
# #obj.send_command()
