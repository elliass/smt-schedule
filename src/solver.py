from z3 import Or, Sum, Optimize, sat
from schedule import TSCHSchedule
from slotframe_fix import Slotframe
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
        self.result_summary = {}


    def get_tsch_parameters(self):
        self.tsch_parameters['max_slots'] = self.max_slots
        self.tsch_parameters['max_channels'] = self.max_channels
        return self.tsch_parameters
    

    def get_solutions(self):
        return self.solutions
    

    def get_result_summary(self):
        return self.result_summary
    

    def solutions_to_string(self):
        solutions_to_string = []
        for solution in self.solutions:
            solution_to_string = {} 
            solution_to_string['timeslot'] = solution.get_timeslot_to_string()
            solution_to_string['channel'] = solution.get_channel_to_string()
            solutions_to_string.append(solution_to_string)
        return solutions_to_string


    def find_feasible_schedules(self, max_slots, max_channels, retries):
        # Initialize TSCH schedule
        tsch_schedule = TSCHSchedule(self.network, max_slots, max_channels)
        timeslots, channels = tsch_schedule.get_timeslots_channels()
        nodes = self.network.get_nodes()
        edges = self.network.get_edges()
        edges_str = self.network.get_edges_str()
        communications = self.network.get_communication()
        
        # Compute and return all model constraints
        constraints = tsch_schedule.compute()
        
        # Create Z3 solver and add constraints
        solver = Optimize()
        # solver = Solver()
        for constraint in constraints:
            solver.add(constraint)

        # Set objective function to minimize timeslot
        solver.minimize(Sum(timeslots))
        # solver.minimize(Sum(channels))

        # Evaluate model
        counter = 0

        # Iterate over each pair of slot_assignment and channel_assignment
        while counter < self.max_solutions and solver.check() == sat:
            solution = Slotframe()

            # Get the model with the assigned values
            model = solver.model()
            
            # Retrieve the assignments for each communication
            timeslot_values = [ model.evaluate(timeslots[i]) for i in range(len(edges)) ]
            channel_values = [ model.evaluate(channels[i]) for i in range(len(edges)) ]

            # Add the solution to the list
            solution.set_timeslot(timeslot_values)
            solution.set_channel(channel_values)
            self.solutions.append(solution)

            # Add blocking clause to prevent finding the same solution again
            blocking_clauses = [Or(timeslots[i] != timeslot_values[i], channels[i] != channel_values[i]) for i in range(len(edges))]
            blocking_clause = Or(blocking_clauses)
            solver.add(blocking_clause)

            counter += 1
        
        self.result_summary = {
            'nb_nodes': len(nodes),
            'nb_edges': len(edges),
            'nb_communications': len(communications),
            'nb_solutions': len(self.solutions),
            'nb_constraints': len(constraints),
            'nb_slots': max_slots,
            'nb_channels': max_channels,
            'nb_retries': retries,
            'edges': edges_str,
            'communications': communications,
            'solutions': self.solutions_to_string(),
        }
        return self.solutions, self.result_summary
    

    def run_solver(self):
        # Capture the start time
        start_time = time.time()

        # Run solver while solution not found or max retries reached (set to 5)
        found = False
        retries = 0
        while not found and retries < self.max_retries:
            print(f"max_slots: {self.max_slots}, max_channels: {self.max_channels}, retries: {retries}")
            solutions, result_summary = self.find_feasible_schedules(self.max_slots, self.max_channels, retries)
            if len(solutions) > 0:
                found = True
            else:
                self.max_slots += 1 
                retries += 1
                # if retries % 3 == 0:
                self.max_channels += 1 

        # Capture the end time and compute the elapsed time
        end_time = time.time()
        self.result_summary['processing_time'] = end_time - start_time
        if not found:
            self.result_summary['retries'] = "Number of maximum retries reached"
    