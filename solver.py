from z3 import Solver, Int, And, Or, sat

class TSCHSolver:
    def __init__(self, topology, max_solutions):
        self.topology = topology
        self.max_solutions = max_solutions
        self.model_constraints = []
        self.concurrency_constraints = []
        self.timeslot_concurrency = []
        self.channel_concurrency = []

    def get_constraint(self):
        return self.model_constraints
    
    def add_constraint(self, constraints):
        # for constraint in constraints:
        #     self.model_constraints.append(constraint)
        self.model_constraints.extend(constraints)

    def get_assignments(self):
        # Define variables to represent the assignment of each communication
        edges = self.topology.get_edges()
        assignments = [(Int(f"{edge}_timeslot"), Int(f"{edge}_channel")) for edge in edges]
        
        return assignments
    
    def get_timeslots_channels(self):
        # Unpack assignments into separate lists for timeslots and channels
        assignments = self.get_assignments()
        timeslots, channels = zip(*assignments)

        return timeslots, channels
    
    def set_default_constraint(self):
        timeslots, channels = self.get_timeslots_channels()
        
        # Each edge is assigned a timeslot value from 0 to MAX_SLOTS and a channel value from 0 to MAX_CHANNELS
        time_domain_constraint = [ And(0 <= timeslots[i], timeslots[i] <= self.topology.MAX_SLOTS) for i in range(self.topology.MAX_EDGES) ]
        frequency_domain_constraint = [ And(0 <= channels[i], channels[i] <= self.topology.MAX_CHANNELS) for i in range(self.topology.MAX_EDGES) ]

        # Cell (0,0) is reserved for CAP and always equal to 0
        cap_constraint = [ And(timeslots[0] == 0, channels[0] == 0)]

        # Channel offset 0 is reserved for shared communications
        shared_constraint = [ channels[i] != 0 for i in range(self.topology.MAX_EDGES) if i != 0]

        # Add default constraints to the model
        self.add_constraint([ time_domain_constraint, frequency_domain_constraint, cap_constraint, shared_constraint ])
    
    # Convert string or list of strings to int
    def to_int(self, args):
        if isinstance(args, list):
            return [int(arg[1]) for arg in args]
        else:
            return int(args[1])

    # Define dependency between two edges
    def set_dependency_constraint(self, u, v):
        timeslots, _ = self.get_timeslots_channels()
        dependency_constraint = [ timeslots[self.to_int(u)] > timeslots[self.to_int(v)] ]
        self.add_constraint(dependency_constraint)

    # Define conflict between two edges
    def set_conflict_constraint(self, u, v):
        timeslots, _ = self.get_timeslots_channels()
        conflict_constraint = [ timeslots[self.to_int(u)] != timeslots[self.to_int(v)] ]
        self.add_constraint(conflict_constraint)
    
    # Define allowed concurrency
    def set_concurrency(self, u, v):
        timeslots, channels = self.get_timeslots_channels()
        timeslot_condition = (timeslots[self.to_int(u)] != timeslots[self.to_int(v) ])     # may be on the same timeslot (remove from distinct constraint)
        channel_condition = (channels[self.to_int(u)] != channels[self.to_int(v) ])        # should be on different channels (add to constraint)
        # self.concurrency_constraints.append([ timeslot_concurrency, channel_concurrency ])
        self.timeslot_concurrency.append(timeslot_condition)
        self.channel_concurrency.append(channel_condition)

    def get_concurrency(self):
        return self.concurrency_constraints
    
    def get_timeslot_concurrency(self):
        return self.timeslot_concurrency
    
    def get_channel_concurrency(self):
        return self.channel_concurrency
    
    def set_concurrency_constraint(self):
        timeslots, _ = self.get_timeslots_channels()
        timeslot_concurrency = self.get_timeslot_concurrency()
        channel_concurrency = self.get_channel_concurrency()

        # Each edge is assigned a unique timeslot value
        # # unique_timeslot_constraint = [ Distinct([timeslots[i] for i in range(MAX_EDGES)]) ]
        unique_timeslot_constraint = [ timeslots[i] != timeslots[j] for i in range(self.topology.MAX_EDGES) for j in range(i+1, self.topology.MAX_EDGES) ]    
        
        # Except for concurrent edges (Remove constraint from unique (distinct) constraint)
        timeslot_constraint = [i for i in unique_timeslot_constraint if i not in timeslot_concurrency]

        # Concurrent edges are assigned different channel offsets (inequality added to constraints)
        channel_constraint = channel_concurrency

        # Add timeslot and channel constraints to the model
        self.add_constraint([ timeslot_constraint, channel_constraint ])

    # Define feasible TSCH schedules
    def find(self):
        timeslots, channels = self.get_timeslots_channels()
        edges = self.topology.get_edges()
        
        """-------------------------------------------------------""" 
        # Define assertion contraints NOT USED YET
        assert_timeslot_constraint = [ 
            timeslots[1] == 5, 
            timeslots[3] == 3,
            timeslots[3] == timeslots[4],
        ]
        self.add_constraint(assert_timeslot_constraint)
        """-------------------------------------------------------"""

        # Set constraints
        self.set_default_constraint()
        self.set_concurrency_constraint()
        constraints = self.get_constraint()

        # Create Z3 solver and add constraints
        solver = Solver()
        for constraint in constraints:
            solver.add(constraint)

        # Evaluate model
        solutions = []
        counter = 0

        # Iterate over each pair of slot_assignment and channel_assignment
        while counter < self.max_solutions and solver.check() == sat:
            solution = {}

            # Get the model with the assigned values
            model = solver.model()
            
            # Retrieve the assignments for each communication
            timeslot_values = [ model.evaluate(timeslots[i]) for i in range(len(edges)) ]
            channel_values = [ model.evaluate(channels[i]) for i in range(len(edges)) ]

            # Add the solution to the list
            solution['timeslot_assignment'] = timeslot_values
            solution['channel_assignment'] = channel_values
            solutions.append(solution)

            # Add blocking clause to prevent finding the same solution again
            blocking_clauses = [Or(timeslots[i] != timeslot_values[i], channels[i] != channel_values[i]) for i in range(len(edges))]
            blocking_clause = Or(blocking_clauses)
            solver.add(blocking_clause)

            counter += 1
        
        return solutions