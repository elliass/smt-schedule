from z3 import Solver, Int, Or, Sum, If, Optimize, sat
from TSCHSchedule import TSCHSchedule
from Solution import Solution
from Exception import CapException, DependencyException, ConcurrencyException
import time

class TSCHSolver:
    def __init__(self, network, max_solutions, max_slots, max_channels, max_retries):
        self.network = network
        self.max_solutions = max_solutions
        self.max_slots = max_slots
        self.max_channels = max_channels
        self.max_retries = max_retries
        self.model_constraints = []
        self.tsch_parameters = {}
        self.solutions = []

    def get_tsch_parameters(self):
        self.tsch_parameters['max_slots'] = self.max_slots
        self.tsch_parameters['max_channels'] = self.max_channels
        return self.tsch_parameters

    def find_feasible_schedules(self, max_slots, max_channels, retries):
        # Initialize TSCH schedule
        tsch_schedule = TSCHSchedule(self.network, max_slots, max_channels)
        timeslots, channels = tsch_schedule.get_timeslots_channels()
        edges = self.network.get_edges()
        
        # Compute and return all model constraints
        constraints = tsch_schedule.compute()

        # Create Z3 solver and add constraints
        solver = Optimize()
        # solver = Solver()
        for constraint in constraints:
            solver.add(constraint)

        # Set objective function to minimize timeslot
        solver.minimize(Sum(timeslots))

        # Evaluate model
        counter = 0

        # Iterate over each pair of slot_assignment and channel_assignment
        while counter < self.max_solutions and solver.check() == sat:
            solution = Solution()

            # Get the model with the assigned values
            model = solver.model()
            
            # Retrieve the assignments for each communication
            timeslot_values = [ model.evaluate(timeslots[i]) for i in range(len(edges)) ]
            channel_values = [ model.evaluate(channels[i]) for i in range(len(edges)) ]

            # Add the solution to the list
            solution['timeslot_assignment'] = timeslot_values
            solution['channel_assignment'] = channel_values
            self.solutions.append(solution)

            # Add blocking clause to prevent finding the same solution again
            blocking_clauses = [Or(timeslots[i] != timeslot_values[i], channels[i] != channel_values[i]) for i in range(len(edges))]
            blocking_clause = Or(blocking_clauses)
            solver.add(blocking_clause)

            counter += 1
        # Return solutions, nb_constraints, slotframe_parameters, processing time
        result_summary = {
            'nb_solutions': len(self.solutions),
            'nb_constraints': len(constraints),
            'nb_slots': max_slots,
            'nb_channels': max_channels,
            'nb_retries': retries
        }
        return self.solutions, result_summary
    
    def run_solver(self):
        # Capture the start time
        start_time = time.time()

        # Run solver while solution not found or max retries reached (set to 5)
        found = False
        retries = 0
        while not found and retries < self.max_retries:
            solutions, result_summary = self.find_feasible_schedules(self.max_slots, self.max_channels, retries)
            if len(solutions) > 0:
                found = True
            else:
                self.max_slots += 1 
                self.max_channels += 1 
                retries += 1

        # Capture the end time and compute the elapsed time
        end_time = time.time()
        result_summary['processing_time'] = end_time - start_time
        if not found:
            result_summary['retries'] = "Number of maximum retries reached"
        return solutions, result_summary
    
    def verify(self, solution):
        ts, ch = solution['timeslot_assignment'], solution['channel_assignment']
        edges = self.network.get_edges()
        errors = []
        # try:
        for tsi, edgei in zip(ts, edges):
            # Check shared constraint
            if not edgei.is_cap() and tsi == 0: #edgei.name != 'e0'
                error_message = f"Shared error raised with Timselot['{edgei}'] = {tsi}"
                errors.append(error_message)
                # raise CapException(edgei)
            for tsj, edgej in zip(ts, edges):
                nodei1, nodei2 = edgei.get_node1(), edgei.get_node2()
                nodej1, nodej2 = edgej.get_node1(), edgej.get_node2()
                # Check dependency constraints
                if nodei1.is_tag() and nodej1.is_anchor() and nodei2 == nodej1:
                    if int(tsi.as_long()) >= int(tsj.as_long()):
                        error_message = f"Dependency error raised with Timselot['{edgei}'] >= Timselot['{edgej}']"
                        errors.append(error_message)
                        # raise DependencyException(edgei, edgej)
                # Check concurrency constraints
                if edgei != edgej and int(tsi.as_long()) == int(tsj.as_long()):
                    if edgei != edgej and int(tsi.as_long()) == int(tsj.as_long()):
                        nodes = {nodei1, nodei2, nodej1, nodej2}
                        if len(nodes) < 4: 
                            error_message = f"Concurrency error raised with Timselot['{edgei}'] = Timselot['{edgej}']"
                            errors.append(error_message)
                            # raise ConcurrencyException(edgei, edgej)
        return errors
        # except CapException as e:
        #     print("Caught CapException:", str(e))
        # except DependencyException as e:
        #     print("Caught DependencyException:", str(e))
        # except ConcurrencyException as e:
        #     print("Caught ConcurrencyException:", str(e))
    
    def display(self, solution):
        ts_list, ch_list = solution['timeslot_assignment'], solution['channel_assignment']
        edges = self.network.get_edges()
        for ts, ch, edge in zip(ts_list, ch_list, edges):
            print(f"('{edge}',{ts},{ch}),")
        
    def summarize(self, result_summary):
        print("+-------------------------------+")
        print("| Solution summary              |")
        print("+-------------------------------+")
        print(f"-> Processing time: {result_summary['processing_time']} seconds")
        print(f"-> Solutions found: {result_summary['nb_solutions']}")
        print(f"-> Number of constraints: {result_summary['nb_constraints']}")
        print(f"-> Number of timeslots: {result_summary['nb_slots']}")
        print(f"-> Number of channels: {result_summary['nb_channels']}")
        print(f"-> Number of retries: {result_summary['nb_retries']}")
    
    def assess_quality(self): 
        print("+-------------------------------+")
        print("| Slotframe quality assessement |")
        print("+-------------------------------+")
        slotframe_length = self.get_tsch_parameters()['max_slots'] + 1
        slotframe_width = self.get_tsch_parameters()['max_channels'] + 1
        timeslots_used  = 0
        channels_used = 0
        cells_available = slotframe_length * slotframe_width
        cells_used = len(self.network.get_edges())
        occupancy_rate = cells_used / cells_available
        timeslot_occupancy_rate = timeslots_used / slotframe_length
        channel_occupancy_rate = channels_used / slotframe_width
        print(f"-> Number of cells available: {cells_available}")
        print(f"-> Number of cells used: {cells_used}")
        print(f"-> Slotframe occupancy rate: {round(occupancy_rate, 2) * 100} %")
        print(f"-> Timeslot occupancy rate: {round(timeslot_occupancy_rate, 2) * 100} %")
        print(f"-> Channel occupancy rate: {round(channel_occupancy_rate, 2) * 100} %")
