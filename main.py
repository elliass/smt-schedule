from z3 import (
    Solver, Int, Array, IntSort, sat, Distinct, Implies, Or, And, AtMost, If, Sum, Bool, Not
)

print()

####################################################################
# Define helper functions
####################################################################
# Display assignment ouptut as a list of timeslot and channel offset  
def print_lists(ts_list, ch_list):
    print(f"ts: {ts_list}")
    print(f"ch: {ch_list}")
        
# Display assignment ouptut as a tuple for each edge
def print_edges(ts_list, ch_list, edges):
    for i, edge in enumerate(edges):
        print(f"{edge}: ({ts_list[i]},{ch_list[i]})")

# Convert string or list of strings to int
def to_int(args):
    if isinstance(args, list):
        args_int = []
        for arg in args:
            args_int.append(int(arg[1]))
        return args_int
    else:
        return int(args[1])

# Define dependency between two edges
def DependsOn(u, v, timeslots):
   return [ timeslots[to_int(u)] > timeslots[to_int(v)] ]

# Define conflict between two edges
def ConflictsWith(u, v, timeslots):
    return [ timeslots[to_int(u)] != timeslots[to_int(v)] ]

def find_feasible_slots(edges, timeslots, channels, model_constraints, max_solutions, MAX_EDGES, MAX_SLOTS, MAX_CHANNELS):
    ####################################################################
    # Define model constraints
    ####################################################################
    # Constraint 1: each edge is assigned a timeslot value from 0 to MAX_SLOTS and a channel value from 0 to MAX_CHANNELS
    time_domain_constraint = [ And(0 <= timeslots[i], timeslots[i] <= MAX_SLOTS) for i in range(MAX_EDGES) ]
    channel_domain_constraint = [ And(0 <= channels[i], channels[i] <= MAX_CHANNELS) for i in range(MAX_EDGES) ]

    # Constraint 2: each edge is assigned a unique timeslot value except for the forwarding edge (e3 can have any value)
    unique_timeslot_constraint = [ Distinct([timeslots[i] for i in range(MAX_EDGES - 1)]) ]

    # Constraint 3: each edge is assigned a unique channel offset value
    unique_channel_constraint = [ Distinct([channels[i] for i in range(MAX_EDGES)]) ]

    # Constraint 4: cell (0,0) is reserve for CAP and always equal to 0
    cap_constraint = [ And(timeslots[0] == 0, channels[0] == 0)]

    # Define additional constraints based on your specific requirements
    default_constraints = [
        time_domain_constraint,
        channel_domain_constraint,
        unique_timeslot_constraint,
        unique_channel_constraint,
        cap_constraint,
    ]

    constraints = default_constraints + model_constraints


    ####################################################################
    # Create solver and add constraints
    ####################################################################
    s = Solver()
    for constraint in constraints:
        s.add(constraint)


    ####################################################################
    # Evaluate model
    ####################################################################
    # Iterate over each pair of slot_assignment and channel_assignment
    solutions = []
    counter = 0

    while counter < max_solutions and s.check() == sat:
        solution = {}

        # Get the model with the assigned values
        model = s.model()
        
        # Retrieve the assignments for each communication
        # assigned_values = [model.evaluate(assignments[i]) for i in range(len(edges))]
        timeslot_values = [ model.evaluate(timeslots[i]) for i in range(len(edges)) ]
        channel_values = [ model.evaluate(channels[i]) for i in range(len(edges)) ]

        # Add the solution to the list
        # solutions.append(assigned_values)
        solution['timeslot_assignment'] = timeslot_values
        solution['channel_assignment'] = channel_values
        solutions.append(solution)

        # # Add blocking clause to prevent finding the same solution again
        blocking_clauses = [Or(timeslots[i] != timeslot_values[i], channels[i] != channel_values[i]) for i in range(len(edges))]
        blocking_clause = Or(blocking_clauses)
        s.add(blocking_clause)

        counter += 1
    
    return solutions


####################################################################
# Define topology variables
####################################################################
# Define main topology variables
"""
Communications: 2 ranging, 1 forwarding
    e0 = cap (t1 <-> a1)
    e1 = ranging (t1 -> a1)
    e2 = ranging (t1 -> a2)
    e3 = forwarding (a2 -> a1)

"""
# MAX_NODES = 3       # {t1,a1,a2}
# MAX_EDGES = 4       # {e0,e1,e2,e3} 
# MAX_SLOTS = 3       # {ts0,ts1,ts2,ts3}
# MAX_CHANNELS = 3    # {ch0,ch1,ch2,ch3}

"""
Communications: 3 ranging, 2 forwarding
    e0 = cap (t1 <-> a1)
    e1 = ranging (t1 -> a1)
    e2 = ranging (t1 -> a2)
    e3 = ranging (t1 -> a3)
    e4 = forwarding (a2 -> a1)
    e5 = forwarding (a3 -> a1)
"""
MAX_NODES = 4       # {t1,a1,a2,a3}
MAX_EDGES = 6       # {e0,e1,e2,e3,e4,e5}
MAX_SLOTS = 5       # {ts0,ts1,ts2,ts3,ts4,ts5}
MAX_CHANNELS = 5    # {ch0,ch1,ch2,ch3,ch4,ch5}

# Define the list of communication represented with edges
edges = ['e0', 'e1', 'e2', 'e3', 'e4', 'e5']

# Define variables to represent the assignment of each communication
assignments = [(Int(f"{edge}_timeslot"), Int(f"{edge}_channel")) for edge in edges]

# Unpack assignments into separate lists for timeslots and channels
timeslots, channels = zip(*assignments)


####################################################################
# Define topology constraints
####################################################################
model_constraints = []

# Dependency constraint: a forwarding communication can not occur before its related ranging communication
dependency_constraint = [ 
    DependsOn('e4', 'e2', timeslots),       # (i.e. e4 > e2)
    DependsOn('e5', 'e3', timeslots),
]

# Conflict constraint: a communication cannot occur if the is receiver already busy
transciever_constraint = [ 
    ConflictsWith('e4', 'e1', timeslots),   # (i.e.  e4 != e1)
    ConflictsWith('e5', 'e1', timeslots),
    ConflictsWith('e5', 'e4', timeslots),
]

for constraint in dependency_constraint:
    model_constraints.append(constraint)

for constraint in transciever_constraint:
    model_constraints.append(constraint)


####################################################################
# Solve scheduling problem
####################################################################
# Define the maximum number of solutions to find
max_solutions = 100

# Find feasible slots
feasible_slots = find_feasible_slots(edges, timeslots, channels, model_constraints, max_solutions, MAX_EDGES, MAX_SLOTS, MAX_CHANNELS)
for idx, solution in enumerate(feasible_slots):
    print(f"--- Solution {idx+1} ---")
    print_edges(solution['timeslot_assignment'], solution['channel_assignment'], edges)
    print()

"""
--- Solution 1 (ok)         --- Solution 2 (ok)         --- Solution 100 (ok)
e0: (0,0)                   e0: (0,0)                   e0: (0,0)
e1: (1,1)                   e1: (5,2)                   e1: (5,1)
e2: (2,2)                   e2: (1,1)                   e2: (1,4)
e3: (3,3)                   e3: (2,3)                   e3: (2,5)
e4: (4,4)                   e4: (3,5)                   e4: (3,3)
e5: (5,5)                   e5: (4,4)                   e5: (4,2)

5 __ __ __ __ __ e5         5 __ __ __ e4 __ __         5 __ __ e3 __ __ __
4 __ __ __ __ e4 __         4 __ __ __ __ e5 __         4 __ e2 __ __ __ __     
3 __ __ __ e3 __ __         3 __ __ e3 __ __ __         3 __ __ __ e4 __ __     
2 __ __ e2 __ __ __         2 __ __ __ __ __ e1         2 __ __ __ __ e5 __     
1 __ e1 __ __ __ __         1 __ e2 __ __ __ __         1 __ __ __ __ __ e1     
0 e0 __ __ __ __ __         0 e0 __ __ __ __ __         0 e0 __ __ __ __ __     
  0  1  2  3  4  5            0  1  2  3  4  5            0  1  2  3  4  5      

Communications: 3 ranging, 2 forwarding 
e0 = cap (t1 <-> a1)
e1 = ranging (t1 -> a1)
e2 = ranging (t1 -> a2)
e3 = ranging (t1 -> a3)
e4 = forwarding (a2 -> a1)
e5 = forwarding (a3 -> a1)

5 __ __ __ __ __ __
4 __ __ __ __ __ __
3 __ __ __ __ __ __
2 __ __ __ __ __ __
1 __ __ __ __ __ __
0 __ __ __ __ __ __
  0  1  2  3  4  5 
"""