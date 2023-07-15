from NetworkTopology import NetworkTopology
from Node import Tag, Anchor
import json

# Read JSON file with topology definition
with open('input.json', 'r') as file:
    cells = json.load(file)

for cell_key, cell_value in cells.items():
    tags = cell_value.get("tags", [])
    anchors = cell_value.get("anchors", [])
    parent =  ["t1","a1"]
    ranging = cell_value.get("ranging", [])
    forwarding = cell_value.get("forwarding", [])
    cap = cell_value.get("cap", [])
    # print(cell_key)
    # print("Tags:", tags, "- Anchors:", anchors, "- Parent:", parent)

    # Initialize nodes
    tag_nodes = [ Tag(tag) for tag in tags ]
    anchors_nodes = [ Anchor(anchors) for anchors in anchors ]

    # Add nodes to network topology
    network = NetworkTopology()
    nodes = tag_nodes + anchors_nodes
    for node in nodes:
        network.add_node(node)

    # Add connections edges
    for edge in ranging + cap:
        node1, node2 = edge[0], edge[1]
        network.add_edges(Tag(node1), Anchor(node2))
    
    for edge in forwarding:
        node1, node2 = edge[0], edge[1]
        network.add_edges(Anchor(node1), Anchor(node2))
    
    for i in network.get_edges():
        print(i.get_nodes())
