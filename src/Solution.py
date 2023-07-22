from prettytable import PrettyTable, FRAME, ALL

class Solution:
    def __init__(self, network):
        self.network = network
        self.timeslot_assignment = []
        self.channel_assignment = []
    
    def set_timeslot(self, timeslot_assignment):
        self.timeslot_assignment = timeslot_assignment
    
    def get_timeslot(self):
        return self.timeslot_assignment
        
    def set_channel(self, channel_assignment):
        self.channel_assignment = channel_assignment
        
    def get_channel(self):
        return self.channel_assignment
    
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


    def display_solution(self, solution):
        ts_list, ch_list = solution['timeslot_assignment'], solution['channel_assignment']
        edges = self.network.get_edges()
        for ts, ch, edge in zip(ts_list, ch_list, edges):
            # print(f"('{edge}',{ts},{ch}),")
            print(f"{edge}: ({ts},{ch})")
