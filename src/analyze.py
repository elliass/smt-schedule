import json
import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import pandas as pd


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

FOLDER = "binary_tree"
logs = read_from_json(f"../definition/{FOLDER}/output/logs.json")
summary_file = f"../definition/{FOLDER}/output/summary.txt"
table_file = f"../definition/{FOLDER}/output/table.txt"
write_to_text("", summary_file)
myTable = PrettyTable(["Id", "Topology", "Edges", "Constraints", "Timeslots", "Channels", "Cells available", "Cells used", "Occupancy rate", "Processing time", "Found"])
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

    myTable.add_row([idx, key, int(value["nb_edges"]), int(value["nb_constraints"]), int(value.get("nb_slots", "")), int(value.get("nb_channels", "")), int(cells_available), int(cells_used), int(round(occupancy_rate, 2) * 100), round(float(value.get("processing_time", "")), 3), int(value.get("nb_solutions", ""))])
    idx += 1 

append_to_text(str(myTable), summary_file)
write_to_text(str(myTable), table_file)
print(myTable)


# df = pd.DataFrame.from_records(myTable.rows, columns=myTable.field_names)
# print(df)

# df_edges = df['Occupancy rate'] 
# fig = df_edges.plot(kind='bar', figsize=(5, 3), fontsize=14).get_figure()
# fig.savefig('../out/Edges.png')
# plt.show()

# for col in df.columns:
#     if col != "Topology":
#         file_name = col.replace(" ", "_")
#         print(col)
#         fig = df[col].plot(kind='bar', figsize=(5, 3), fontsize=14).get_figure()
#         fig.savefig(f'../out/plots/{file_name}.png')

# fig1 = df['Edges'].plot(kind='bar', figsize=(5, 3), fontsize=14).get_figure()
# fig1.savefig(f'../out/plots/edges.png')

# fig2 = df['Constraints'].plot(kind='bar', figsize=(5, 3), fontsize=14).get_figure()
# fig2.savefig(f'../out/plots/constraints.png')

# fig3 = df['Cells available'].plot(kind='bar', figsize=(5, 3), fontsize=14).get_figure()
# fig3.savefig(f'../out/plots/cells_available.png')

# fig = df['Cells used'].plot(kind='bar', figsize=(5, 3), fontsize=14).get_figure()
# fig.savefig(f'../out/plots/cells_used.png')

# fig = df['Occupancy rate'].plot(kind='bar', figsize=(5, 3), fontsize=14).get_figure()
# fig.savefig(f'../out/plots/occupancy_rate.png')