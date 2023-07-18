# from NetworkTopology import NetworkTopology
from NetworkTopology import NetworkTopology
from Node import Tag, Anchor, Node
import json

# Read JSON file with topology definition
with open('../input.json', 'r') as file:
    cells = json.load(file)

for cell_key, cell_value in cells.items():
    tags = cell_value.get("tags", [])
    anchors = cell_value.get("anchors", [])
    parent =  cell_value.get("parent", "")
    cap = cell_value.get("cap", [])

    # Initialize nodes
    tag_nodes = [ Tag(tag) for tag in tags ]
    anchors_nodes = [ Anchor(anchor) for anchor in anchors ]

    for anchor in anchors_nodes:
        if anchor.name == parent:
            parent_node = anchor


    # Add nodes to network topology
    network = NetworkTopology()
    nodes = tag_nodes + anchors_nodes
    for node in nodes:
        network.add_node(node)
    
    # Add cap communications
    for tag_node in tag_nodes:
        network.add_edges(tag_node, parent_node)

    # Add ranging communications
    for tag_node in tag_nodes:
        for anchor_node in anchors_nodes:
            network.add_edges(tag_node, anchor_node)
    
    # Add forwarding communications
    for child_node in anchors_nodes:
        if child_node != parent_node:
            network.add_edges(child_node, parent_node)

    # result = []
    # for nodei in network.get_nodes():
    #     communications = [ communication.name for communication in nodei.get_communication()]
    #     diff = list(set(communications).symmetric_difference(set(result)))
    #     result = communications
    #     print(nodei, communications, diff)

        # for nodej in network.get_nodes():
        #     if nodei != nodej:
        #         communicationsj = [ communication.name for communication in nodej.get_communication()]
        #         result = list(set(communicationsi).symmetric_difference(set(communicationsj)))
        #         print(f"{nodej}: {communicationsj} --> {result}")
        
    t1 = ['e0', 'e1', 'e2', 'e3']
    a1 = ['e0', 'e1', 'e4', 'e5']
    a2 = ['e2', 'e4']
    a3 = ['e3', 'e5']

    diff = list(set(t1).symmetric_difference(set(a1)))
    diff = list(set(diff).symmetric_difference(set(a2)))
    diff = list(set(diff).symmetric_difference(set(a3)))

    print(diff)

    # for node in network.get_nodes():
    #     for communication in node.get_communication():
    #         if communication.is_ranging():
    #             tag = communication.get_tag()
    #         if communication.is_forwarding() and node == communication.get_child():
    #             payload = f"measure_{tag}"
    #             node.set_queue(payload)
    #             print(f"{node}: {node.get_queue()}")


    # print(network.get_communication_from_node(network.get_nodes()[0]))



# output = [
#     ('e0', (0, 0)),
#     ('e1', (2, 2)),
#     ('e2', (3, 0)),
#     ('e3', (2, 1)),
#     ('e4', (1, 2))
# ]



# l = [('0','0'),('0','0'),('0','0'), ('0','0')]
# width = max(len(e) for t in l for e in t[:-1]) + 1 
# format=('%%-%ds' % width) * len(l[0])
# print('\n'.join(format % tuple(t) for t in l))