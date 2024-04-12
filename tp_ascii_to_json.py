import sys
import re
import json


def convert_to_json(input_file, output_file):
    data = {}
    with open(input_file, 'r') as f:
        lines = f.readlines()
        lines = [line.strip(' ') for line in lines]

    # Extracting title and variables
    data['TITLE'] = lines[0].split('=')[1].strip()

    # grab lines specifying vars
    var_startline = lines.index([str(line) for line in lines if str(line).startswith("VARIABLES")][0])
    var_endline = lines.index([str(line) for line in lines[var_startline+1:] if not str(line).startswith('"')][0])
    vars = [str(line).split('"')[1] for line in lines[var_startline:var_endline]]
    # print("vars = ", vars)    

    # specify structure
    structure_line = [str(line).split('=') for line in lines if line.startswith(r'I=')][0]

    # point, block, timestrand data needs implementation, for now assumes non-transient ordered point data
    
    data_start = lines.index([line for line in lines[var_endline:] if line[0].isdigit()][0])
    var_lists = [[] for var in vars]

    for line in lines[data_start:]:
        # split line
        if line.endswith('\n'):
            line = line.strip('\n')
        values = line.split(' ')

        # should be same number of values as variables on each line in point format
        for i, value in enumerate(values):
            #print(value)
            var_lists[i].append(value)

    data["VARIABLES"] = dict(zip(vars, var_lists))
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_to_json(input_file, output_file)