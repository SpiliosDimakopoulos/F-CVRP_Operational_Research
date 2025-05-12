class SolutionValidator:
    def __init__(self, model, routes):
        """
        Initialize the validator with the model and solution routes
        """
        self.model = model
        self.routes = routes
        
    def validate(self):
        """
        Validate if the solution satisfies all problem constraints
        Returns True if valid, False otherwise
        """
        # Check if number of routes doesn't exceed available vehicles
        if len(self.routes) > self.model.num_vehicles:
            print(f"Error: Too many routes ({len(self.routes)}) - max allowed: {self.model.num_vehicles}")
            return False
        
        # Get all nodes in the solution
        all_nodes = [node for route in self.routes for node in route]
        
        # Check for duplicates in the solution
        if len(all_nodes) != len(set(all_nodes)):
            print("Error: Some nodes appear multiple times in the solution")
            return False
        
        # Check family constraints
        family_counts = [0] * self.model.num_families
        for node in all_nodes:
            family = self.model.family_assignment[node]
            family_counts[family] += 1
        
        for family_idx in range(self.model.num_families):
            required = self.model.required_per_family[family_idx]
            if family_counts[family_idx] != required:
                print(f"Error: Family {family_idx} has {family_counts[family_idx]} nodes, but {required} are required")
                return False
        
        # Check capacity constraints
        for route_idx, route in enumerate(self.routes):
            total_demand = 0
            for node in route:
                family = self.model.family_assignment[node]
                total_demand += self.model.demands[family]
            
            if total_demand > self.model.capacity:
                print(f"Error: Route {route_idx} exceeds capacity ({total_demand} > {self.model.capacity})")
                return False
        
        # All checks passed
        return True
