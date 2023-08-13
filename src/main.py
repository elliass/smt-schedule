import argparse
import random
import time
import os

from scheduling.network import NetworkTopology
from scheduling.node import Tag, Anchor
from scheduling.solver import UWBTSCHSolver

from utils.files import read_from_json, write_to_json, write_to_text, get_topology_files

class Main:
    def __init__(self, max_solutions=1, max_slots=4, max_channels=1, max_retries=5):
        self.max_solutions = max_solutions
        self.max_slots = max_slots
        self.max_channels = max_channels
        self.max_retries = max_retries
        self.network = NetworkTopology()
        self.tsch_solver = UWBTSCHSolver(self.network, max_solutions, self.max_slots, self.max_channels, self.max_retries)

    def setup_network_topology(self, input_file):
        cells = read_from_json(input_file)

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

            # Add forwarding communications
            self.setup_forwarding_tree()

    def traverse_node_tree(self, node, root):
        if node.is_anchor() and node.name != root:
            self.network.add_edges(node, node.parent)
            self.traverse_node_tree(node.parent, root)

    def setup_forwarding_tree(self):
        root = "a1"
        for node in self.network.get_nodes():
            if node.is_anchor() and node.name != root:
                self.traverse_node_tree(node, root)

    def run_tsch_algorithm(self):
        self.tsch_solver.run_solver()

    def select_random_slotframe(self):
        solutions = self.tsch_solver.get_solutions()
        n = random.randint(0, len(solutions) - 1)
        return solutions[n]

    def register_slotframe(self, slotframe):
        for edge, timeslot, channel in zip(self.network.get_edges(), slotframe.get_timeslot(), slotframe.get_channel()):
            edge.set_cell(timeslot, channel)

    def simulate_UWB_TSCH(self):
        timeslot_duration = 0.5
        results = self.tsch_solver.get_result_summary()
        slotframe_length = int(results['nb_slots']) + 1
        asn = 0
        while True:
            for timeslot in range(slotframe_length):
                print(f"--- Timeslot {timeslot} (ASN {asn}) ---")
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
                asn += 1

    def output_communications(self, path):
        edges = self.network.get_edges()
        header = "+-------------------------------+\n" + "| Network communications        |\n" + "+-------------------------------+"
        data = header
        for communication in edges:
            if communication.is_ranging():
                data = data + f"\nRAN {communication} | {communication.get_node1()} <-> {communication.get_node2()}"
            if communication.is_forwarding():
                data = data + f"\nFOR {communication} | {communication.get_node1()} -> {communication.get_node2()}"
        # print(data)
        write_to_text(data, f"{path}/communications.txt")

    def output_slotframe(self, slotframe, path):
        table = slotframe.show_as_table(self.network.get_edges(), self.network.get_communication())
        header = "+-------------------------------+\n" + "| Slotframe                     |\n" + "+-------------------------------+"
        data = header + "\n" + str(table)
        # print(data)
        write_to_text(data,  f"{path}/slotframe.txt")

    def output_logs(self, topology, path, logs={}):
        results = self.tsch_solver.get_result_summary()
        solutions = results["solutions"]
        logs[topology] = results
        write_to_json(logs, f"{path}/logs.json")
        write_to_json(solutions, f"{path}/solutions.json")


if __name__ == "__main__":
    # Handle arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--topology", type=str, default="default", help="run scheduling alogrithm for specified topology")
    parser.add_argument("--watch", action='store_true', help="run with UWB-TSCH network simulation")
    args = parser.parse_args()

    # Get topology file
    if args.topology:
        try:
            FOLDER = args.topology
            input_path = os.path.join("../in/", FOLDER)
            output_path = os.path.join("../out/", FOLDER)
            topology_files = get_topology_files(input_path)
        except FileNotFoundError:
            print("File provided was not found.")
            raise SystemExit("Please enter a valid topology...")
    
    # Trigger algorithm execution
    for topology_file in topology_files:
        print(f"Running scheduling algorithm for topology: {topology_file}")

        # Initialize network and solver parameters
        main = Main(max_solutions=1, max_slots=4, max_channels=1, max_retries=20)
        network = main.network
        tsch_solver = main.tsch_solver

        # Setup network topology and forwarding tree
        main.setup_network_topology(topology_file)

        # Trigger TSCH algorithm and show solutions
        main.run_tsch_algorithm()

        # Export logs
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        file = os.path.basename(topology_file)
        main.output_logs(file, output_path)

        # Select slotframe
        slotframe = main.select_random_slotframe()

        # Export topology and slotframe
        main.output_communications(output_path)
        main.output_slotframe(slotframe, output_path)

        # Control network over selected slotframe
        if args.watch:
            print(f"*** Starting network simulation")
            try:
                while True:
                    main.register_slotframe(slotframe)
                    main.simulate_UWB_TSCH()
            except KeyboardInterrupt:
                print("\n*** End of simulation")