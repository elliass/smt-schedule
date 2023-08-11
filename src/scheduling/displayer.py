from scheduling.network import NetworkTopology
from scheduling.solver import TSCHSolver

class Displayer:
    def __init__(self, network:NetworkTopology, tsch_solver:TSCHSolver):
        self.network = network
        self.tsch_solver = tsch_solver

    def verify_all_solutions(self):
        solutions = self.tsch_solver.get_solutions()
        edges = self.network.get_edges()
        for solution in solutions:
            results = solution.verify_slotframe(edges)
            if results.__contains__(False):
                return False
        return True
    
    def display_all_solutions(self):
        print("+-------------------------------+")
        print("| All solutions                 |")
        print("+-------------------------------+")
        solutions = self.tsch_solver.get_solutions()
        edges = self.network.get_edges()
        for idx, solution in enumerate(solutions):
            print(f"---------- Solution {idx+1} ----------")
            results = solution.verify_slotframe(edges)
            if results.__contains__(False):
                print("Solution is not verified")
                break
            solution.display_solution(edges)

    def display_network(self):
        print("+-------------------------------+")
        print("| Network communications        |")
        print("+-------------------------------+")
        # nodes = self.network.get_nodes()
        # for node in self.get_nodes():
        #     communications = [ communication.name for communication in node.get_communication()]
            # print(f"{node}: {communications}")

        edges = self.network.get_edges()
        for communication in edges:
            # if communication.is_cap(): REMOVED CAP
            #     print(f"CAP {communication} | {communication.get_node1()} <-> {communication.get_node2()}")
            if communication.is_ranging():
                print(f"RAN {communication} | {communication.get_node1()} <-> {communication.get_node2()}")
            if communication.is_forwarding():
                print(f"FOR {communication} | {communication.get_node1()} -> {communication.get_node2()}")

    def analyze_logs(self, logs):
        for key, log in logs.items():
            print("\n+-------------------------------+")
            print(f"| Log summary {key}     |")
            print("+-------------------------------+")
            print("|> Solver summary")
            print(f"  * Processing time: {log['processing_time']} seconds")
            print(f"  * Solutions found: {log['nb_solutions']}")
            print(f"  * Number of edges: {log['nb_edges']}")
            print(f"  * Number of constraints: {log['nb_constraints']}")
            print(f"  * Number of timeslots: {log['nb_slots']}")
            print(f"  * Number of channels: {log['nb_channels']}")
            print(f"  * Number of retries: {log['nb_retries']}")

            slotframe_length = log['nb_slots'] # not + 1 because timeslot 0 reserved for shared communications
            slotframe_width = log['nb_channels'] + 1
            cells_available = slotframe_length * slotframe_width
            cells_used = log['nb_edges']
            occupancy_rate = cells_used / cells_available

            print("\n|> Slotframe quality assessement")
            print(f"  * Number of cells available: {cells_available}")
            print(f"  * Number of cells used: {cells_used}")
            print(f"  * Slotframe occupancy rate: {round(occupancy_rate, 2) * 100} %")

    def get_analysis(self, logs):
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
        return data