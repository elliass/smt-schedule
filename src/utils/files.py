import json
import os

def read_from_json(input_file):
    # Read JSON file with topology definition
    with open(input_file, 'r') as file:
        data = json.load(file)
    return data

def write_to_json(data, output_file):
    # Write JSON results
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=2, separators=(',',': '))

def write_to_text(data, output_file):
    # Write output to text file
    with open(output_file, 'w') as file:
        file.write(data)

def get_topology_files(path):
    topology_files = []
    for file in sorted(os.listdir(path)):
        if file.endswith(".json"):
            topology_files.append(os.path.join(path, file))
    return topology_files