from NetworkTopology import NetworkTopology
from TSCHSolver import TSCHSolver
from prettytable import PrettyTable, ALL

class Displayer:
    def __init__(self, network:NetworkTopology, tsch_solver:TSCHSolver):
        self.network = network
        self.tsch_solver = tsch_solver
    
    def show_as_table(self, data):
        # List of tuples to display in matrix
        data = [
            ('e0',2,0),
        ('e1',3,0),
        ('e2',1,1),
        ('e3',2,2),
        ('e4',3,3),
        ('e5',1,0),
        ('e6',6,2),
        ('e7',5,0),
        ('e8',2,3),
        ('e9',4,3),
        ]

        # Extract the x, y, and value components from the tuples
        values, x_coords, y_coords = zip(*data)

        # Determine the size of the matrix based on the maximum x and y coordinates
        max_x = max(x_coords)
        max_y = max(y_coords)
        matrix_size = (max_y + 1, max_x + 1)

        # Create a PrettyTable instance
        table = PrettyTable(header=True, hrules=ALL, horizontal_char="-", align="c")

        # Create a dictionary to store the values at their corresponding positions
        matrix_dict = {(x, y): value for value, x, y in data}

        # Add rows to the table without column headers
        for y in reversed(range(matrix_size[0])):
            row_data = [matrix_dict.get((x, y), '') for x in range(matrix_size[1])]
            table.add_row(['channel ' + str(y)] + row_data)

        # Rename the headers
        headers = ['ch/ts'] + ['slot ' + str(x) for x in range(matrix_size[1])]
        table.field_names = headers

        # Print the table
        print(table)

    
    def verify_all_solutions(self):
        solutions = self.tsch_solver.get_solutions()
        edges = self.network.get_edges()
        for solution in solutions:
            results = solution.verify_solution(edges)
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
            results = solution.verify_solution(edges)
            if results.__contains__(False):
                print("Solution is not verified")
                break
            solution.display_solution(edges)


    def summarize(self):
        result_summary = self.tsch_solver.get_result_summary()
        print("+-------------------------------+")
        print("| Solver summary                |")
        print("+-------------------------------+")
        print(f"-> Processing time: {result_summary['processing_time']} seconds")
        print(f"-> Solutions found: {result_summary['nb_solutions']}")
        print(f"-> Number of constraints: {result_summary['nb_constraints']}")
        print(f"-> Number of timeslots: {result_summary['nb_slots']}")
        print(f"-> Number of channels: {result_summary['nb_channels']}")
        print(f"-> Number of retries: {result_summary['nb_retries']}")
    

    def assess_quality(self): 
        tsch_parameters = self.tsch_solver.get_tsch_parameters()
        edges = self.network.get_edges()
        print("+-------------------------------+")
        print("| Slotframe quality assessement |")
        print("+-------------------------------+")
        slotframe_length = tsch_parameters['max_slots'] + 1
        slotframe_width = tsch_parameters['max_channels'] + 1
        timeslots_used  = 0
        channels_used = 0
        cells_available = slotframe_length * slotframe_width
        cells_used = len(edges)
        occupancy_rate = cells_used / cells_available
        timeslot_occupancy_rate = timeslots_used / slotframe_length
        channel_occupancy_rate = channels_used / slotframe_width
        print(f"-> Number of cells available: {cells_available}")
        print(f"-> Number of cells used: {cells_used}")
        print(f"-> Slotframe occupancy rate: {round(occupancy_rate, 2) * 100} %")
        print(f"-> Timeslot occupancy rate: {round(timeslot_occupancy_rate, 2) * 100} %")
        print(f"-> Channel occupancy rate: {round(channel_occupancy_rate, 2) * 100} %")


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