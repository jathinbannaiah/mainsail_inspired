with open(r"/home/j2002/vl53l1_register_map.py", "r") as file1, open(r"/home/j2002/test_file.py", "w") as file2:
    for line in file1:
        if line.startswith("#"):
            line = line.split()
            print(line)
            try:
                new_line = line[1] + "=" + line[2] + "\n"
                file2.write(new_line)
            except:
                pass
