from z3 import Int, And, Or, If

class Schedule:
    def __init__(self, network, max_slots, max_channels):
        self.network = network
        self.max_slots = max_slots
        self.max_channels = max_channels
        
        self.default_constraints = []
        self.dependency_constraints = []
        self.conflict_constraints = []
        self.timeslot_constraints = []
        self.channel_constraints = []
        self.model_constraints = []

    def get_assignments(self):
        # Define variables to represent the assignment of each communication
        edges = self.network.get_edges_str()
        assignments = [(Int(f"{edge}_timeslot"), Int(f"{edge}_channel")) for edge in edges]
        return assignments
    
    def get_timeslots_channels(self):
        # Unpack assignments into separate lists for timeslots and channels
        assignments = self.get_assignments()
        timeslots, channels = zip(*assignments)
        return timeslots, channels
    
    def add_constraint(self, constraint):
        self.model_constraints.extend(constraint)
    
    def get_constraint(self):
        flattened_constraints = [constraint for constraint_list in self.model_constraints for constraint in constraint_list]
        return flattened_constraints
    
    def compute(self):
        constraints = [
            self.get_dependency_constraints(),
            self.get_conflict_constraints(),
            self.get_default_constraints(),
            self.get_timeslot_constraints(),
            self.get_channel_constraints(),
        ]
        self.add_constraint(constraints)
        return self.get_constraint()

    def get_default_constraints(self):
        timeslots, channels = self.get_timeslots_channels()
        edges = self.network.get_edges()
        
        # Each edge is assigned a timeslot value from 0 to MAX_SLOTS and a channel value from 0 to MAX_CHANNELS
        time_domain_constraint = [ And(0 <= timeslots[i], timeslots[i] <= self.max_slots) for i in range(len(edges)) ]
        frequency_domain_constraint = [ And(0 <= channels[i], channels[i] <= self.max_channels) for i in range(len(edges)) ]

        # Timeslot 0 is reserved for shared communications
        shared_constraint = [ timeslots[i] != 0 for i in range(len(edges)) ]

        # Add default constraints to the model
        constraint = time_domain_constraint + frequency_domain_constraint + shared_constraint
        self.default_constraints.extend(constraint)
        return self.default_constraints
    
    def to_int(self, args):
        """ Convert string or list of strings to int
        :param args: string or list[string] such ['e1', 'e2']
        :return: int or list[int] such [1,2]
        """
        if isinstance(args, list):
            return [int(arg[1:]) for arg in args]
        else:
            return int(args[1:])
    
    def get_dependency_constraints(self):
        timeslots, _ = self.get_timeslots_channels()
        communications = self.network.get_communication()
        edges = self.network.get_edges()
        for edge_u, communication_u in zip(edges, communications):
            for edge_v, communication_v in zip(edges, communications):
                _, node_u = communication_u
                node_v, _ = communication_v
                if node_u == node_v:
                    constraints = [ timeslots[self.to_int(edge_u.name)] < timeslots[self.to_int(edge_v.name)] ]
                    self.dependency_constraints.extend(constraints)
        return self.dependency_constraints
    
    def get_conflict_constraints(self):
        timeslots, _ = self.get_timeslots_channels()
        communications = self.network.get_communication()
        edges = self.network.get_edges()
        for edge_u, communication_u in zip(edges, communications):
            for edge_v, communication_v in zip(edges, communications):
                node_u, node_s = communication_u
                node_t, node_v = communication_v
                if (node_u == node_v or node_u == node_t or node_v == node_s) and edge_u != edge_v:
                    constraints = [ timeslots[self.to_int(edge_u.name)] != timeslots[self.to_int(edge_v.name)] ]
                    self.conflict_constraints.extend(constraints)  

        # Remove duplicated constraints
        # for u in range(len(edges)):
        #     edge_u = edges[u]
        #     communication_u = communications[u]
        #     node_u, node_s = communication_u
        #     for v in range(u, len(edges)):
        #         edge_v = edges[v]
        #         communication_v = communications[v]
        #         node_t, node_v = communication_v
        #         if (node_u == node_v or node_u == node_t or node_v == node_s) and edge_u != edge_v:
                    # # constraints = [ timeslots[self.to_int(edge_u.name)] != timeslots[self.to_int(edge_v.name)] ]
                    # # self.conflict_constraints.extend(constraints)  
                    # print([ timeslots[self.to_int(edge_u.name)] != timeslots[self.to_int(edge_v.name)] ])  

        return self.conflict_constraints
    
    def get_timeslot_constraints(self):
        timeslots, _ = self.get_timeslots_channels()
        communications = self.network.get_communication()
        edges = self.network.get_edges()
        allowed_timeslot_constraints = []
        for edge_u, communication_u in zip(edges, communications):
            for edge_v, communication_v in zip(edges, communications):
                node_u, node_s = communication_u
                node_t, node_v = communication_v
                if (node_u != node_v and node_u != node_t and node_v != node_s) and edge_u != edge_v: # and edge_u.is_forwarding():
                    allowed_timeslot_constraints.extend([ timeslots[self.to_int(edge_v.name)] != timeslots[self.to_int(edge_u.name)] ])

        # Each edge is assigned a unique timeslot value
        unique_timeslot_constraints = [ timeslots[i] != timeslots[j] for i in range(len(edges)) for j in range(i+1, len(edges)) ]    

        # Except for concurrent edges (Remove constraint from unique (distinct) constraint)
        constraints = [i for i in unique_timeslot_constraints if i not in allowed_timeslot_constraints]
        
        self.timeslot_constraints.extend(constraints)  
        return self.timeslot_constraints
    
    def get_channel_constraints(self):
        timeslots, channels = self.get_timeslots_channels()
        communications = self.network.get_communication()
        edges = self.network.get_edges()
        restricted_channel_constraints = []
        for edge_u, communication_u in zip(edges, communications):
            for edge_v, communication_v in zip(edges, communications):
                node_u, node_s = communication_u
                node_t, node_v = communication_v
                if (node_u != node_v and node_u != node_t and node_v != node_s) and edge_u != edge_v: # and edge_u.is_forwarding():
                    restricted_channel_constraints.extend([ 
                        If(
                            timeslots[self.to_int(edge_v.name)] == timeslots[self.to_int(edge_u.name)], 
                            channels[self.to_int(edge_v.name)] != channels[self.to_int(edge_u.name)],
                            Or(channels[self.to_int(edge_v.name)] != channels[self.to_int(edge_u.name)], channels[self.to_int(edge_v.name)] == channels[self.to_int(edge_u.name)])
                        )
                    ]) 

        # Remove duplicated constraints
        # for u in range(len(edges)):
        #     edge_u = edges[u]
        #     communication_u = communications[u]
        #     node_u, node_s = communication_u
        #     for v in range(u, len(edges)):
        #         edge_v = edges[v]
        #         communication_v = communications[v]
        #         node_t, node_v = communication_v
        #         if (node_u != node_v and node_u != node_t and node_v != node_s) and edge_u != edge_v: # and edge_u.is_forwarding():
        #             restricted_channel_constraints.extend([ 
        #                 If(
        #                     timeslots[self.to_int(edge_v.name)] == timeslots[self.to_int(edge_u.name)], 
        #                     channels[self.to_int(edge_v.name)] != channels[self.to_int(edge_u.name)],
        #                     Or(channels[self.to_int(edge_v.name)] != channels[self.to_int(edge_u.name)], channels[self.to_int(edge_v.name)] == channels[self.to_int(edge_u.name)])
        #                 )
        #             ]) 

        # Concurrent edges are assigned different channel offsets (inequality added to constraints)
        constraints = restricted_channel_constraints

        self.channel_constraints.extend(constraints)  
        return self.channel_constraints
