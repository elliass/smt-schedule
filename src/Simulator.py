from NetworkTopology import NetworkTopology
from Node import Tag, Anchor
from TSCHSolver import TSCHSolver
from Displayer import Displayer

import json
import random
import time
from z3 import IntVal


class Main:
    def __init__(self, max_solutions=1, max_slots=4, max_channels=1, max_retries=5):
        self.max_solutions = max_solutions
        self.max_slots = max_slots
        self.max_channels = max_channels
        self.max_retries = max_retries
        self.network = NetworkTopology()
        self.tsch_solver = TSCHSolver(self.network, max_solutions, self.max_slots, self.max_channels, self.max_retries)
    

    def read_topology(self, input_file):
        # Read JSON file with topology definition
        with open(input_file, 'r') as file:
            cells = json.load(file)
        return cells


    def setup_network_topology(self, input_file):
        cells = self.read_topology(input_file)

        for cell_key, cell_value in cells.items():
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
            
            # # Add cap communications REMOVED CAP
            # for tag_node in tag_nodes:
            #     self.network.add_edges(tag_node, parent_node)

            # Add ranging communications
            for tag_node in tag_nodes:
                for anchor_node in anchors_nodes:
                    self.network.add_edges(tag_node, anchor_node)


    def traverse_node_tree(self, node, root):
        if node.is_anchor() and node.name != root:
            # print(f"{node} -> {node.parent}")
            self.network.add_edges(node, node.parent)
            self.traverse_node_tree(node.parent, root)


    def setup_forwarding_tree(self):
        root = "a1"
        for node in self.network.get_nodes():
            if node.is_anchor() and node.name != root:
                self.traverse_node_tree(node, root)


    def run_tsch_algorithm(self):
        # Find feasible solutions
        # solutions, result_summary = self.tsch_solver.run_solver()
        self.tsch_solver.run_solver()


    def select_random_solution(self):
        # n = random.randint(0, len(solutions) - 1)
        solutions = self.tsch_solver.get_solutions()
        n = 0
        return solutions[n]
    

    def simulate_network_activity(self, slotframe, slotframe_length):
        timeslot_duration = 1
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
                    # time.sleep(timeslot_duration)
                else:
                    idx = int(edge.name[1:])
                    slotframe['timeslot_assignment'][idx] = IntVal(timeslot)
                    errors = self.tsch_solver.verify(slotframe)
                    # print(errors)
                    # if len(errors) == 0:
                    #     print(f"Alternative slot available on ts={edge_timeslot}, ch={edge_channel} for {edge}")
                    # else:
                    #     print('Conflict with at least one constraint')
                        # print(edge.name, timeslot, True)
                        # transmission = node1.exchange(node2, payload)
                        # print(f"{edge}: {transmission} on ts={edge_timeslot}, ch={edge_channel}")


if __name__ == "__main__":
    # Initialize network and solver parameters
    main = Main(max_solutions=1, max_slots=4, max_channels=1, max_retries=20)
    network = main.network
    tsch_solver = main.tsch_solver

    # Setup network topology and forwarding tree
    main.setup_network_topology('../input.json')
    main.setup_forwarding_tree()

    # Trigger TSCH algorithm and show solutions
    main.run_tsch_algorithm()

    # Display and verify solutions
    displayer = Displayer(network, tsch_solver)
    displayer.display_all_solutions()
    verified = displayer.verify_all_solutions()

    # Display network communications
    displayer.display_network()

    # Display scheduling algorithm results
    displayer.summarize()
    displayer.assess_quality()

    # Display selected solution
    slotframe = main.select_random_solution()
    slotframe.show_as_table(network.get_edges())
    
    # # Assign TSCH cells to each edge and simulate network activity
    # slotframe_length = int(result_summary['nb_slots']) + 1
    # slotframe = main.select_random_slotframe(solutions)
    # assigned_timeslots = slotframe['timeslot_assignment']
    # assigned_channels = slotframe['channel_assignment']
    # for edge, timeslot, channel in zip(main.network.get_edges(), assigned_timeslots, assigned_channels):
    #     edge.set_cell(timeslot, channel)
    # main.simulate_network_activity(slotframe, slotframe_length)






    # # Show anchor queue
    # for node in main.network.get_nodes():
    #     for communication in node.get_communication():
    #         if communication.is_forwarding():
    #             print(f"{node}: {node.get_queue()}")



    


