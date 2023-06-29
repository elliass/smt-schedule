from topology import Topology
from solver import TSCHSolver

# Display assignment ouptut as a tuple for each edge
def print_edges(ts_list, ch_list, edges):
    for i, edge in enumerate(edges):
        print(f"{edge}: ({ts_list[i]},{ch_list[i]})")

# Define main function running TSCH algorithm to find feasible schedules
def main(tsch):
    # Find feasible solutions
    feasible_slots = tsch.find()

    # Display solutions
    for idx, solution in enumerate(feasible_slots):
        print(f"--- Solution {idx+1} ---")
        print_edges(solution['timeslot_assignment'], solution['channel_assignment'], topology.get_edges())
        print()

# Define topology and TSCH solver
"""
Communications: 3 ranging, 2 forwarding 
e0 = cap (t1 <-> a1)
e1 = ranging (t1 -> a1)
e2 = ranging (t1 -> a2)
e3 = ranging (t1 -> a3)
e4 = forwarding (a2 -> a1)
e5 = forwarding (a3 -> a1)
"""
MAX_NODES = 4                                   # number of node in the network: {t1,a1,a2,a3}
MAX_EDGES = 6                                   # number of edges between nodes: {e0,e1,e2,e3,e4,e5}
MAX_SLOTS = 5                                   # number of timeslots in the TSCH schedule: {ts0,ts1,ts2,ts3,ts4,ts5}
MAX_CHANNELS = 5                                # number of channels in the TSCH schedule: {ch0,ch1,ch2,ch3,ch4,ch5} 
topology = Topology(MAX_EDGES, MAX_SLOTS, MAX_CHANNELS)
tsch = TSCHSolver(topology, max_solutions=1)    # maximum number of solutions to return by the SMT solver

# Set topology constraints
tsch.set_dependency_constraint('e4', 'e2')      # e4 relies on e2 -> e4 must be scheduled in a timeslot after e2
tsch.set_dependency_constraint('e5', 'e3')          
tsch.set_conflict_constraint('e4', 'e1')        # e4 conflicts with e1 -> e4 must be scheduled in a different timeslot than e1
tsch.set_conflict_constraint('e5', 'e1')
tsch.set_conflict_constraint('e5', 'e4')
tsch.set_concurrency('e3', 'e4')                # e3 independent from e4 -> e3 and e4 can be scheduled in the same timeslot
tsch.set_concurrency('e2', 'e5')

main(tsch)