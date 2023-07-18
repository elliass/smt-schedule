from NetworkTopology import NetworkTopology
from Node import Tag, Anchor
from TSCHSolver import TSCHSolver
import json

class SlotframeGenerator:
    def __init__(self, max_solutions=1, max_slots=4, max_channels=1):
        self.network = NetworkTopology()
        self.max_solutions = max_solutions
        self.max_slots = max_slots
        self.max_channels = max_channels
        self.tsch_solver = TSCHSolver(self.network, max_solutions, self.max_slots, self.max_channels)

    def setup_topology(self):
        # Read JSON file with topology definition
        with open('../input.json', 'r') as file:
            cells = json.load(file)

        for cell_key, cell_value in cells.items():
            tags = cell_value.get("tags", [])
            anchors = cell_value.get("anchors", [])
            parent =  cell_value.get("parent", "")

            # Initialize nodes
            tag_nodes = [ Tag(tag) for tag in tags ]
            anchors_nodes = [ Anchor(anchors) for anchors in anchors ]

            # Set parent node
            for anchor in anchors_nodes:
                if anchor.name == parent:
                    parent_node = anchor

            # Add nodes to network topology
            nodes = tag_nodes + anchors_nodes
            for node in nodes:
                self.network.add_node(node)
            
            # Add cap communications
            for tag_node in tag_nodes:
                self.network.add_edges(tag_node, parent_node)

            # Add ranging communications
            for tag_node in tag_nodes:
                for anchor_node in anchors_nodes:
                    self.network.add_edges(tag_node, anchor_node)
            
            # Add forwarding communications
            for child_node in anchors_nodes:
                if child_node != parent_node:
                    self.network.add_edges(child_node, parent_node)

    def run_tsch_algorithm(self):
        # Implement the logic to run the TSCH algorithm and display results
        # Find feasible solutions
        solutions, result_summary = self.tsch_solver.run_solver()

        # Display solutions
        for idx, solution in enumerate(solutions):
            # print(f"--- Solution {idx+1} ---")
            # self.tsch_solver.display(solution)
            # print()
            results = self.tsch_solver.verify(solution)
            if results.__contains__(False):
                print("+-------------------------------+")
                print("| Solution is not verified      |")
                print("+-------------------------------+")
                break

        # Print last solution found
        found = len(solutions)
        if found > 0:
            print(f"--- Solution {found} ---")
            self.tsch_solver.display(solutions[found-1])
            print()
            # print("+-------------------------------+")
            # print("| All solutions are verified    |")
            # print("+-------------------------------+")

        self.tsch_solver.summarize(result_summary)
        self.tsch_solver.assess_quality()


if __name__ == "__main__":
    main = Main(max_solutions=1, max_slots=4, max_channels=1)
    main.setup_topology()
    main.run_tsch_algorithm()
