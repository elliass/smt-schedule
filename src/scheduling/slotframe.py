from prettytable import PrettyTable, ALL
from scheduling.exception import SharedException, DependencyException, ConcurrencyException

class Slotframe:
    def __init__(self):
        self.timeslot_assignment = []
        self.channel_assignment = []
    
    def set_timeslot(self, timeslot_assignment):
        self.timeslot_assignment = timeslot_assignment
    
    def get_timeslot(self):
        return self.timeslot_assignment
    
    def get_timeslot_to_string(self):
        timeslot_assignment_to_string = []
        for timeslot in self.timeslot_assignment:
            timeslot_assignment_to_string.append(timeslot.as_long())
        return timeslot_assignment_to_string
        
    def set_channel(self, channel_assignment):
        self.channel_assignment = channel_assignment
        
    def get_channel(self):
        return self.channel_assignment
    
    def get_channel_to_string(self):
        channel_assignment_to_string = []
        for channel in self.channel_assignment:
            channel_assignment_to_string.append(channel.as_long())
        return channel_assignment_to_string
    
    def show_as_table(self, edges, communications):
        # List of tuples to display in matrix
        data = self.get_solution(edges, communications)
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
        return table

    def display_solution(self, edges):
        timeslots, channels = self.get_timeslot(), self.get_channel()
        for timeslot, channel, edge in zip(timeslots, channels, edges):
            print(" " * 10 , f"{edge}: ({timeslot},{channel})")
    
    def get_solution(self, edges, communications):
        timeslots, channels = self.get_timeslot(), self.get_channel()
        data = []
        for timeslot, channel, edge, communication in zip(timeslots, channels, edges, communications):
            value = f"{edge}: {communication[0]} -> {communication[1]}"
            tuple_solution = (value, int(timeslot.as_long()), int(channel.as_long()))
            data.append(tuple_solution)
        return data

    def verify_slotframe(self, edges):
        timeslots, channels = self.get_timeslot(), self.get_channel()
        errors = []
        for tsi, chi, edgei in zip(timeslots, channels, edges):
            # Check shared constraints
            if not edgei.is_cap() and tsi == 0:
                error_message = f"Shared error raised with timselot['{edgei}'] = {tsi}"
                errors.append(SharedException(edgei, error_message))
            for tsj, chj, edgej in zip(timeslots, channels, edges):
                nodei1, nodei2 = edgei.get_node1(), edgei.get_node2()
                nodej1, nodej2 = edgej.get_node1(), edgej.get_node2()
                # Check dependency constraints
                if nodei1.is_tag() and nodej1.is_anchor() and nodei2 == nodej1:
                    if int(tsi.as_long()) >= int(tsj.as_long()):
                        error_message = f"Dependency error raised with timselot['{edgei}'] >= timselot['{edgej}']"
                        errors.append(DependencyException(edgei, edgej, error_message))
                # Check concurrency constraints
                if edgei != edgej and int(tsi.as_long()) == int(tsj.as_long()):
                    nodes = {nodei1, nodei2, nodej1, nodej2}
                    if len(nodes) < 4: 
                        error_message = f"Concurrency error raised with timselot['{edgei}'] = timselot['{edgej}']"
                        errors.append(ConcurrencyException(edgei, edgej, error_message))
                    if int(chi.as_long()) == int(chj.as_long()):
                        print(nodei1, nodei2, nodej1, nodej2)
                        error_message = f"Concurrency error raised with channel['{edgei}'] = channel['{edgej}']"
                        errors.append(ConcurrencyException(edgei, edgej, error_message))
        return errors
    
    # Remove duplicated exceptions
    # def verify_slotframe(self, edges):
    #     timeslots, channels = self.get_timeslot(), self.get_channel()
    #     errors = []
    #     for i in range(len(edges)):
    #         edgei, tsi, chi = edges[i], timeslots[i], channels[i]
    #         # Check shared constraints
    #         if not edgei.is_cap() and tsi == 0:
    #             error_message = f"Shared error raised with timselot['{edgei}'] = {tsi}"
    #             errors.append(SharedException(edgei, error_message))
    #         for j in range(i, len(edges)):
    #             edgej, tsj, chj = edges[j], timeslots[j], channels[j]
    #             nodei1, nodei2 = edgei.get_node1(), edgei.get_node2()
    #             nodej1, nodej2 = edgej.get_node1(), edgej.get_node2()
    #             # Check dependency constraints
    #             if nodei1.is_tag() and nodej1.is_anchor() and nodei2 == nodej1:
    #                 if int(tsi.as_long()) >= int(tsj.as_long()):
    #                     error_message = f"Dependency error raised with timselot['{edgei}'] >= timselot['{edgej}']"
    #                     errors.append(DependencyException(edgei, edgej, error_message))
    #             # Check concurrency constraints
    #             if edgei != edgej and int(tsi.as_long()) == int(tsj.as_long()):
    #                 nodes = {nodei1, nodei2, nodej1, nodej2}
    #                 if len(nodes) < 4: 
    #                     error_message = f"Concurrency error raised with timselot['{edgei}'] = timselot['{edgej}']"
    #                     errors.append(ConcurrencyException(edgei, edgej, error_message))
    #                 if int(chi.as_long()) == int(chj.as_long()):
    #                     print(nodei1, nodei2, nodej1, nodej2)
    #                     error_message = f"Concurrency error raised with channel['{edgei}'] = channel['{edgej}']"
    #                     errors.append(ConcurrencyException(edgei, edgej, error_message))
    #     return errors