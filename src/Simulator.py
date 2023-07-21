from NetworkTopology import NetworkTopology
from Node import Tag, Anchor
from TSCHSolver import TSCHSolver
import json
import random
import time
from z3 import IntVal


class Main:
    def __init__(self, max_solutions=1, max_slots=4, max_channels=1, max_retries=5):
        self.network = NetworkTopology()
        self.max_solutions = max_solutions
        self.max_slots = max_slots
        self.max_channels = max_channels
        self.max_retries = max_retries
        self.tsch_solver = TSCHSolver(self.network, max_solutions, self.max_slots, self.max_channels, self.max_retries)
    
    def read_topology(self, input_file):
        # Read JSON file with topology definition
        with open(input_file, 'r') as file:
            cells = json.load(file)
        return cells

    def setup_topology(self, input_file):
        cells = self.read_topology(input_file)

        for cell_key, cell_value in cells.items():
            tags = cell_value.get("tags", [])
            anchors = cell_value.get("anchors", [])
            parent =  cell_value.get("parent", "")
            next_parent =  cell_value.get("next_parent", "")

            # Initialize nodes
            tag_nodes = [ Tag(tag) for tag in tags ]
            anchors_nodes = [ Anchor(anchors) for anchors in anchors ]

            # # Set parent node
            # for anchor in anchors_nodes:
            #     if anchor.name == parent:
            #         parent_node = anchor

            # Add nodes to network topology
            nodes = anchors_nodes + tag_nodes
            for node in nodes:
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
            
            # Add forwarding communications
            for anchor_node in anchors_nodes:
                if anchor_node !=  anchor_node.get_parent(): # exclude root communication a1 -> a1
                    self.network.add_edges(anchor_node, anchor_node.get_parent())

    def run_tsch_algorithm(self):
        # Find feasible solutions
        solutions, result_summary = self.tsch_solver.run_solver()
        return solutions, result_summary

    def display_solutions(self, solutions):
        for idx, solution in enumerate(solutions):
            print(f"--- Solution {idx+1} ---")
            self.tsch_solver.display(solution)
            print()
            results = self.tsch_solver.verify(solution)
            if results.__contains__(False):
                print("+-------------------------------+")
                print("| Solution is not verified      |")
                print("+-------------------------------+")
                break
        print("+-------------------------------+")
        print("| All solutions are verified    |")
        print("+-------------------------------+")

    def verify_solutions(self, solutions):
        for solution in solutions:
            results = self.tsch_solver.verify(solution)
            if results.__contains__(False):
                return False
        return True

    def display_last_solution(self, solutions):
        found = len(solutions)
        if found > 0:
            print(f"--- Solution {found} ---")
            self.tsch_solver.display(solutions[found-1])
            print()

    def analyze_tsch_algorithm(self, result_summary):
        self.tsch_solver.summarize(result_summary)
        self.tsch_solver.assess_quality()

    def select_random_slotframe(self, solutions):
        # n = random.randint(0, len(solutions) - 1)
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

    def display_network(self):
        print("\n--- Network ---")
        for node in self.network.get_nodes():
            communications = [ communication.name for communication in node.get_communication()]
            # print(f"{node}: {communications}")
        
        for communication in self.network.get_edges():
            # if communication.is_cap(): REMOVED CAP
            #     print(f"CAP {communication} | {communication.get_node1()} <-> {communication.get_node2()}")
            if communication.is_ranging():
                print(f"RAN {communication} | {communication.get_node1()} <-> {communication.get_node2()}")
            if communication.is_forwarding():
                print(f"FOR {communication} | {communication.get_node1()} -> {communication.get_node2()}")


if __name__ == "__main__":
    # Initialize network topology
    main = Main(max_solutions=1, max_slots=4, max_channels=1, max_retries=5)
    main.setup_topology('../input.json')

    # Trigger TSCH algorithm and show solutions
    solutions, result_summary = main.run_tsch_algorithm()
    main.display_solutions(solutions)
    # # main.display_last_solution(solutions)
    # # verified = main.verify_solutions(solutions)
    # # print(verified)

    # Display scheduling algorithm results
    main.analyze_tsch_algorithm(result_summary)

    # # Assign TSCH cells to each edge and simulate network activity
    # slotframe_length = int(result_summary['nb_slots']) + 1
    # slotframe = main.select_random_slotframe(solutions)
    # assigned_timeslots = slotframe['timeslot_assignment']
    # assigned_channels = slotframe['channel_assignment']
    # for edge, timeslot, channel in zip(main.network.get_edges(), assigned_timeslots, assigned_channels):
    #     edge.set_cell(timeslot, channel)
    # main.simulate_network_activity(slotframe, slotframe_length)

    # Display network communications
    main.display_network()

    # for c in main.network.get_communication():
    #     print(c)

    # for node in main.network.get_nodes():
    #     if node.is_anchor():
    #         print(node, ":", node.get_parent())




    # # Show anchor queue
    # for node in main.network.get_nodes():
    #     for communication in node.get_communication():
    #         if communication.is_forwarding():
    #             print(f"{node}: {node.get_queue()}")



    


