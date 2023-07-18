from NetworkTopology import NetworkTopology
from Node import Tag, Anchor
from TSCHSolver import TSCHSolver

# Define main function running TSCH algorithm to find feasible schedules
def main(tsch_solver):
    # Find feasible solutions
    solutions, result_summary = tsch_solver.run_solver()

    # Display solutions
    for idx, solution in enumerate(solutions):
        # print(f"--- Solution {idx+1} ---")
        # tsch_solver.display(solution)
        # print()
        results = tsch_solver.verify(solution)
        if results.__contains__(False):
            print("+-------------------------------+")
            print("| Solution is not verified      |")
            print("+-------------------------------+")
            break

    # Print last solution found
    found = len(solutions)
    if found > 0:
        tsch_solver.display(solutions[found-1])
        print()
        # print("+-------------------------------+")
        # print("| All solutions are verified    |")
        # print("+-------------------------------+")

    tsch_solver.summarize(result_summary)
    tsch_solver.assess_quality(result_summary)

# Initialize network topology
network = NetworkTopology()

# +--------+
# | Cell 1 |
# +--------+
# Add nodes
tag1 = Tag("t1")
anchor1 = Anchor("a1")
anchor2 = Anchor("a2")
anchor3 = Anchor("a3")

network.add_node(tag1)
network.add_node(anchor1)
network.add_node(anchor2)
network.add_node(anchor3)

# Add connections
network.add_edges(tag1, anchor1) # CAP
network.add_edges(tag1, anchor1)
network.add_edges(tag1, anchor2)
network.add_edges(tag1, anchor3)
network.add_edges(anchor2, anchor1)
network.add_edges(anchor3, anchor1)

# +--------+
# | Cell 2 |
# +--------+
# Add nodes
tag2 = Tag("t2")
anchor4 = Anchor("a4")
anchor5 = Anchor("a5")
anchor6 = Anchor("a6")

network.add_node(tag2)
network.add_node(anchor4)
network.add_node(anchor5)
network.add_node(anchor6)

# Add connections
network.add_edges(tag2, anchor4)
network.add_edges(tag2, anchor5)
network.add_edges(tag2, anchor6)
network.add_edges(anchor5, anchor4)
network.add_edges(anchor6, anchor4)
network.add_edges(anchor4, anchor1)

# # +--------+
# # | Cell 3 |
# # +--------+
# # Add nodes
# tag3 = Tag("t3")
# anchor7 = Anchor("a7")
# anchor8 = Anchor("a8")
# anchor9 = Anchor("a9")

# network.add_node(tag3)
# network.add_node(anchor7)
# network.add_node(anchor8)
# network.add_node(anchor9)

# # Add connections
# network.add_edges(tag3, anchor7)
# network.add_edges(tag3, anchor8)
# network.add_edges(tag3, anchor9)
# network.add_edges(anchor8, anchor7)
# network.add_edges(anchor9, anchor7)
# network.add_edges(anchor7, anchor1)

# # +--------+
# # | Cell 4 |
# # +--------+
# # Add nodes
# tag4 = Tag("t4")
# anchor10 = Anchor("a10")
# anchor11 = Anchor("a11")
# anchor12 = Anchor("a12")

# network.add_node(tag4)
# network.add_node(anchor10)
# network.add_node(anchor11)
# network.add_node(anchor12)

# # Add connections
# network.add_edges(tag4, anchor10)
# network.add_edges(tag4, anchor11)
# network.add_edges(tag4, anchor12)
# network.add_edges(anchor11, anchor10)
# network.add_edges(anchor12, anchor10)
# network.add_edges(anchor10, anchor1)


# Find feasible schedules
tsch_solver = TSCHSolver(network, max_solutions=1)
main(tsch_solver)



# TO DO: 
# adapt slot size based on topology (see formulas)
# add assertions

"""
e0: ('t1', 'a1') e0 != 1,2,3,4,5    0(self)
e1: ('t1', 'a1') e1 != 0,2,3,4,5    1(self)
e2: ('t1', 'a2') e2 != 0,1,3        2(self),4,5
e3: ('t1', 'a3') e3 != 0,1,2        3(self),4,5
e4: ('a2', 'a1') e4 != 0,1,2,5      3,4(self)
e5: ('a3', 'a1') e5 != 0,1,3,4      2,5(self)
"""