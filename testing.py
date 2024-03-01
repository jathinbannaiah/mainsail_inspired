import struct

x_lenght = 24.989 + 25.00000024
y_lenght = 24.997002 + 24.997002

x_bits_factor = y_bits_factor = 67108863 // 250

with open("./Cli/circle of 50dia v1.cli","r") as file:
    for line in file.readlines():
        if line.startswith("$$POLYLINE/"):
            line = line.split(",")
            l = line[2:]
            print(len(l))

            break
    l2 = []

for item in l:
    item = float(item) *0.005 + 50
    item = item * x_bits_factor
    if item > 67108863 or item < 0:
        print(1)
    l2.append(item)


# with open("./Cli/cmd_database_hatch.txt","w") as file2:
#     for item in l2:
#         file2.write(str(item) +","+ "\n" )

EEEE_bytes = struct.pack('<I', 250000)
for i in range(len(l2)):
    l2[i] = round(l2[i])
with open("./Cli/cmd_database_Z(250000).txt","w") as file2:
    for i in range(0,len(l2),2):
        if i >= (len(l2) -1):
            break
        AAAA_bytes = struct.pack('<I', l2[i])
        BBBB_bytes = struct.pack('<I', l2[i+1])
        command = b'd' + bytes([0x01]) + AAAA_bytes + BBBB_bytes + EEEE_bytes
        if not isinstance(command,bytes):
            print(3)
        if len(command) != 14:
            print(2)
        file2.write(str(command) +","+ "\n" )

    file2.write(str(b'd\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))

