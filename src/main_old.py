from network import NetworkTopology
from node import Tag, Anchor
from solver import TSCHSolver
# from Displayer import Displayer

import json
import random
import time
import os
from z3 import IntVal

FOLDER = "base_cell1"

def get_topology_files(is_analysis=False):
    topology_files = []
    input_directory = f"../definition/base_cell1/input"
    if is_analysis:
        global FOLDER 
        # FOLDER = "one_tag"
        FOLDER = "binary_tree"
        input_directory = f"../definition/{FOLDER}/input"
    for file in sorted(os.listdir(input_directory)):
        if file.endswith(".json"):
            topology_files.append(os.path.join(input_directory, file))
    return topology_files

class Main:
    def __init__(self, max_solutions=1, max_slots=4, max_channels=1, max_retries=5):
        self.max_solutions = max_solutions
        self.max_slots = max_slots
        self.max_channels = max_channels
        self.max_retries = max_retries
        self.network = NetworkTopology()
        self.tsch_solver = TSCHSolver(self.network, max_solutions, self.max_slots, self.max_channels, self.max_retries)
        # self.displayer = Displayer(self.network, self.tsch_solver)
    

    def read_from_json(self, input_file):
        # Read JSON file with topology definition
        with open(input_file, 'r') as file:
            data = json.load(file)
        return data
    

    def write_to_json(self, data, output_file):
        # Write JSON results
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=2, separators=(',',': '))

    
    def write_to_text(self, data, output_file):
        # Write output to text file
        with open(output_file, 'w') as file:
            file.write(data)


    def setup_network_topology(self, input_file):
        cells = self.read_from_json(input_file)

        for _, cell_value in cells.items():
            tags = cell_value.get("tags", [])
            anchors = cell_value.get("anchors", [])
            parent =  cell_value.get("parent", "")
            next_parent =  cell_value.get("next_parent", "")

            # Initialize nodes
            tag_nodes = [ Tag(tag) for tag in tags ]
            anchors_nodes = [ Anchor(anchors) for anchors in anchors ]

            # Add nodes to network topology
            nodes = anchors_nodes + tag_nodes
            for node in nodes:
                found = self.network.find_node_by_name(node.name)
                if found is None:
                    self.network.add_node(node)
            
            # Set parent node
            for node in nodes:
                parent_node = self.network.find_node_by_name(parent)
                next_parent_node = self.network.find_node_by_name(next_parent)
                if node == parent_node:
                    node.set_parent(next_parent_node)
                else:
                    node.set_parent(parent_node)

            # Add ranging communications
            for tag_node in tag_nodes:
                for anchor_node in anchors_nodes:
                    self.network.add_edges(tag_node, anchor_node)


    def traverse_node_tree(self, node, root):
        if node.is_anchor() and node.name != root:
            self.network.add_edges(node, node.parent)
            self.traverse_node_tree(node.parent, root)


    def setup_forwarding_tree(self):
        root = "a1"
        # Add forwarding communications
        for node in self.network.get_nodes():
            if node.is_anchor() and node.name != root:
                self.traverse_node_tree(node, root)


    def run_tsch_algorithm(self):
        self.tsch_solver.run_solver()


    def select_random_slotframe(self):
        # n = random.randint(0, len(solutions) - 1)
        solutions = self.tsch_solver.get_solutions()
        n = 0
        return solutions[n]
    

    def register_slotframe(self, slotframe):
        for edge, timeslot, channel in zip(main.network.get_edges(), slotframe.get_timeslot(), slotframe.get_channel()):
            edge.set_cell(timeslot, channel)


    def simulate_UWB_TSCH(self, slotframe):
        timeslot_duration = 1
        results = main.tsch_solver.get_result_summary()
        slotframe_length = int(results['nb_slots']) + 1
        valid = True
        while valid:
            for timeslot in range(slotframe_length):
                print(f"--- Timeslot {timeslot} ---")
                for edge in self.network.get_edges():
                    node1, node2 = edge.get_node1(), edge.get_node2()
                    edge_timeslot, edge_channel = edge.get_cell()['timeslot'], edge.get_cell()['channel']
                    if edge_timeslot == timeslot :
                        if edge.is_cap():
                            payload = f"CAP_{node1}"
                        if edge.is_ranging():
                            payload = f"ToA_{node1}"
                        if edge.is_forwarding():
                            payload = f"Measurement_{node1}"
                        transmission = node1.exchange(node2, payload)
                        print(f"{edge}: {transmission} on ts={edge_timeslot}, ch={edge_channel}")
                        # print(node2.get_queue())
                        time.sleep(timeslot_duration)
                    else:
                        idx = int(edge.name[1:])
                        slotframe.get_timeslot()[idx] = IntVal(timeslot)
                        errors = slotframe.verify_slotframe(self.network.get_edges())
                        # print(errors)
                        # if len(errors) == 0:
                        #     print(f"Alternative slot available on ts={edge_timeslot}, ch={edge_channel} for {edge}")
                        # else:
                        #     print('Conflict with at least one constraint')
                            # print(edge.name, timeslot, True)
                            # transmission = node1.exchange(node2, payload)
                            # print(f"{edge}: {transmission} on ts={edge_timeslot}, ch={edge_channel}")


    def output_topology(self):
        edges = self.network.get_edges()
        header = "+-------------------------------+\n" + "| Network communications        |\n" + "+-------------------------------+"
        data = header
        for communication in edges:
            if communication.is_ranging():
                data = data + f"\nRAN {communication} | {communication.get_node1()} <-> {communication.get_node2()}"
            if communication.is_forwarding():
                data = data + f"\nFOR {communication} | {communication.get_node1()} -> {communication.get_node2()}"
        # print(data)
        self.write_to_text(data, f"../definition/{FOLDER}/output/topology.txt")


    def output_slotframe(self, slotframe):
        table = slotframe.show_as_table(self.network.get_edges(), self.network.get_communication())
        header = "+-------------------------------+\n" + "| Slotframe                     |\n" + "+-------------------------------+"
        data = header + "\n" + str(table)
        # print(data)
        self.write_to_text(data,  f"../definition/{FOLDER}/output/slotframe.txt")


    def set_logs(self, topology, result_summary):
        logs[topology] = result_summary
    

    def get_logs(self):
        return logs
    

    def output_logs(self, file):
        results = main.tsch_solver.get_result_summary()
        self.set_logs(file, results)
        data = self.get_logs()
        # self.write_to_text(str(data), '../out/logs.txt')
        self.write_to_json(data, f"../definition/{FOLDER}/output/logs.json")


if __name__ == "__main__":
    # Get topology file (or files for sensitivity analysis)
    is_analysis = False
    topology_files = get_topology_files(is_analysis)
    logs = {}

    # Trigger algorithm execution
    for topology_file in topology_files:
        # Initialize network and solver parameters
        main = Main(max_solutions=1, max_slots=4, max_channels=1, max_retries=20)
        network = main.network
        tsch_solver = main.tsch_solver

        # Setup network topology and forwarding tree
        main.setup_network_topology(topology_file)
        main.setup_forwarding_tree()

        # Trigger TSCH algorithm and show solutions
        main.run_tsch_algorithm()

        # Export logs
        file = os.path.basename(topology_file)
        main.output_logs(file)

        # if not is_analysis:
        # Select slotframe
        slotframe = main.select_random_slotframe()

        # Export topology and slotframe
        main.output_topology()
        main.output_slotframe(slotframe)

            # # Control network over selected slotframe
            # main.register_slotframe(slotframe)
            # main.simulate_UWB_TSCH(slotframe)
            
print("folder:", FOLDER)