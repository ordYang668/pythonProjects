import sys

def getValue(line, str):
    value = ""
    index = line.find(str)
    if index != -1:
        end = line.find(" ", index)
        if end == -1:
            end = len(line)
        value = line[index + len(str) : end]
    return value

if len(sys.argv) != 2:
    print("Usage: python3 getexefiles.py ausearchFile")
    sys.exit()

with open(sys.argv[1], 'r') as f:
    lines = f.readlines()

exe = ""
filename = ""

for line in lines:
    # Check for the executable (exe=) in the current line
    if "exe=" in line:
        exe = getValue(line, "exe=")
    
    # Check for the filename (name=) in the current line
    if "name=" in line:
        filename = getValue(line, "name=")

    # Once both exe and filename are found, output and reset
    if exe and filename:
        print(exe + '\t' + filename)
        exe = ""
        filename = ""

