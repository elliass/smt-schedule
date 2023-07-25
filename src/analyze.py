import json

def read_from_json(input_file):
    with open(input_file, 'r') as file:
        cells = json.load(file)
    return cells

def append_to_text(data, output_file):
    with open(output_file, 'a') as file:
        file.write(data)

def write_to_text(data, output_file):
    with open(output_file, 'w') as file:
        file.write(data)

logs = read_from_json('../out/logs.json')
summary_file = '../out/summary.txt'
# write_to_text("", summary_file)

for key, value in logs.items():
    slotframe_length = value.get('nb_slots', "")
    slotframe_width = value.get('nb_channels', "") + 1
    cells_available = slotframe_length * slotframe_width
    cells_used = value.get('nb_edges', "")
    occupancy_rate = cells_used / cells_available
    header = "+-------------------------------+\n" + f"| Summary {key}            |\n" + "+-------------------------------+"
    data = header + \
        '\n- Solver results ' + \
        '\n  - Processing_time: ' + str(value.get("processing_time", "")) + \
        '\n  - Number of edges: ' + str(value.get("nb_edges", "")) + \
        '\n  - Number of communications: ' + str(value.get("nb_communications", "")) + \
        '\n  - Number of solutions: ' + str(value.get("nb_solutions", "")) + \
        '\n  - Number of constraints: ' + str(value.get("nb_constraints", "")) + \
        '\n  - Number of slots: ' + str(value.get("nb_slots", "")) + \
        '\n  - Number of channels: ' + str(value.get("nb_channels", "")) + \
        '\n  - Number of retries: ' + str(value.get("nb_retries", "")) + \
        '\n  - Edges: ' + str(value.get("edges", "")) + \
        '\n  - Communications: ' + str(value.get("communications", "")) + \
        '\n' + \
        '\n- Slotframe quality ' + \
        '\n  - Number of cells available: ' + str(cells_available) + \
        '\n  - Number of cells used: ' + str(cells_used) + \
        '\n  - Slotframe occupancy rate: ' + str(round(occupancy_rate, 2) * 100) + '%' + \
        '\n ' + \
        '\n'
    append_to_text(data, summary_file)