import argparse
import os

from prettytable import PrettyTable

from utils.files import read_from_json, append_to_text, write_to_text

# Handle arguments
parser = argparse.ArgumentParser(description="")
parser.add_argument("--topology", type=str, default="default", help="run analysis for specified topology")
args = parser.parse_args()

# Get topology file
if args.topology:
    try:
        FOLDER = args.topology
        output_path = os.path.join("../out/", FOLDER)
        logs = read_from_json(f"{output_path}/logs.json")
        summary_file = f"{output_path}/summary.txt"
        table_file = f"{output_path}/table.txt"
    except FileNotFoundError:
        print("File provided was not found.")
        raise SystemExit("Please enter a valid topology...")

# Reset file content
write_to_text("", summary_file)

# Generate analysis
myTable = PrettyTable([
    "Id", 
    "Topology", 
    "Edges", 
    "Constraints", 
    "Timeslots", 
    "Channels", 
    "Cells available", 
    "Cells used", 
    "Occupancy rate", 
    "Processing time", 
    "Found"
])

idx = 0
for key, value in logs.items():
    slotframe_length = value.get('nb_slots', "")
    slotframe_width = value.get('nb_channels', "") + 1
    cells_available = slotframe_length * slotframe_width
    cells_used = value.get('nb_edges', "")
    occupancy_rate = cells_used / cells_available
    key = key.replace(".json", "")
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
    myTable.add_row([
        idx, 
        key, 
        int(value["nb_edges"]), 
        int(value["nb_constraints"]), 
        int(value.get("nb_slots", "")), 
        int(value.get("nb_channels", "")), 
        int(cells_available), 
        int(cells_used), 
        int(round(occupancy_rate, 2) * 100), 
        round(float(value.get("processing_time", "")), 3), 
        int(value.get("nb_solutions", ""))
    ])
    idx += 1 

# Write output
append_to_text(str(myTable), summary_file)
write_to_text(str(myTable), table_file)