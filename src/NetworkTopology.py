from UWBCommunication import UWBCommunication, CAP, Ranging, Forwarding
from Node import Node

class NetworkTopology:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.communication = []

    def add_node(self, node:Node):
        self.nodes.append(node)

    def get_nodes(self) -> list[Node]:
        return self.nodes
    
    def find_node_by_name(self, node_name:str):
        for node in self.get_nodes():
            if node.name == node_name:
                return node

    def add_edges(self, node1:Node, node2:Node):
        name = f"e{len(self.get_edges())}"
        if node1.is_tag():
            # if len(node1.get_communication()) == 0: REMOVED CAP #and node1.get_parent() == node2 to make sure it is cap (set parent first)
            #     edge = CAP(node1, node2, name)
            # else:
            edge = Ranging(node1, node2, name)
        else:
            edge = Forwarding(node1, node2, name)
        node1.set_communication(edge)
        node2.set_communication(edge)
        self.edges.append(edge)

    def get_edges(self) -> list[UWBCommunication]:
        return self.edges
    
    def get_communication_from_node(self, node:Node):
        for n in self.get_nodes():
            if node == n:
                communications = [ communication.name for communication in node.get_communication()]
                return communications
        
    def get_edges_str(self):
        edges_str = [ edge.name for edge in self.edges ]
        return edges_str

    def get_communication(self) -> list[str]:
        for edge in self.get_edges():
            node1, node2 = edge.get_nodes()
            self.communication.append(node1.communicate(node2))
        return self.communication

    def get_ranging(self) -> list[UWBCommunication]:
        ranging = [ edge for edge in self.edges if edge.is_ranging()]
        return ranging
    
    def get_forwarding(self) -> list[UWBCommunication]:
        forwarding = [ edge for edge in self.edges if edge.is_forwarding()]
        return forwarding
    
    def display_network(self):
        print("\n--- Network ---")
        # nodes = self.get_nodes()
        # for node in self.get_nodes():
        #     communications = [ communication.name for communication in node.get_communication()]
            # print(f"{node}: {communications}")

        edges = self.get_edges()
        for communication in edges:
            # if communication.is_cap(): REMOVED CAP
            #     print(f"CAP {communication} | {communication.get_node1()} <-> {communication.get_node2()}")
            if communication.is_ranging():
                print(f"RAN {communication} | {communication.get_node1()} <-> {communication.get_node2()}")
            if communication.is_forwarding():
                print(f"FOR {communication} | {communication.get_node1()} -> {communication.get_node2()}")