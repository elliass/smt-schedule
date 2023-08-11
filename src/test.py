import argparse
import json
import os
from z3 import IntVal

from scheduling.network import NetworkTopology
from scheduling.node import Tag, Anchor
from scheduling.slotframe import Slotframe

from utils.files import read_from_json, get_topology_files

class Main:
    def __init__(self):
        self.network = NetworkTopology()

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

    def test_all_solutions(self, input_file):
        solutions = read_from_json(input_file)
        for solution in solutions:
            slotframe = self.convert_schedule(solution)
            result = self.test_solution(slotframe)
            if result == "Test failed":
                # print(result)
                return result
        return "All tests passed" 

    def test_solution(self, solution):
        errors = solution.verify_slotframe(network.get_edges())
        if errors:
            print(f"Schedule broke at least one constraint. \nThe following errors were detected: \n{errors}")
            return "Test failed"
        return "Test passed"

    def convert_schedule(self, arg):
        try:
            if type(arg) is str:
                schedule = json.loads(arg)
            elif type(arg) is dict:
                schedule = arg
            else:
                print("Argument provided is neither a string or dict")
                return None
            solution = Slotframe()
            timeslot_values = [ IntVal(ts) for ts in schedule["timeslot"] ]
            channel_values = [ IntVal(ch) for ch in schedule["channel"] ]
            solution.set_timeslot(timeslot_values)
            solution.set_channel(channel_values)
            return solution
        except Exception:
            return None


if __name__ == "__main__":
    # Handle arguments
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--topology", type=str, default="default", help="run test for specified topology")
    parser.add_argument("--all", action='store_true', help="run test for all solutions generated by main")
    parser.add_argument("--solution", type=str, default="", help="run test for the solution provided by user")
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
        main = Main()
        network = main.network

        # Setup network topology and forwarding tree
        main.setup_network_topology(topology_file)
        
        # Run tests
        if args.all:
            print(f"*** Starting test for all solutions")
            solutions_file = f"{output_path}/solutions.json"
            status = main.test_all_solutions(solutions_file)
            print(f"{status} \n *** End of testing")
        elif args.solution:
            print(f"*** Starting test for solution: {args.solution}")
            slotframe = main.convert_schedule(args.solution)
            if slotframe is not None:
                status = main.test_solution(slotframe)
                print(status)
            else:
                print("Solution argument provided was not recognized. \nPlease enter a valid solution...")
            print(f"*** End of testing")
        else:
            print("No solution was provided. \nPlease enter a valid solution...")
