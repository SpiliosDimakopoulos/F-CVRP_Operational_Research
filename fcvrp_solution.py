"""
F-CVRP Solver
Team: Κώστας, Μαρία, Γιώργος
Course: Αλγόριθμοι Βελτιστοποίησης
Date: May 12, 2025

This program solves the Family Capacitated Vehicle Routing Problem (F-CVRP).
"""

import random
import time
from parser import Parser
from solution_validator import SolutionValidator

# Set a seed for reproducibility
SEED = 42
random.seed(SEED)

class FCVRP:
    def __init__(self, filename="fcvrp_P-n101-k4_10_3_3.txt"):
        # Load data from file
        self.parser = Parser(filename)
        self.model = self.parser.load_model()
        
        # Extract data from model
        self.num_nodes = self.model.num_nodes
        self.num_families = self.model.num_families
        self.num_required = self.model.num_required
        self.capacity = self.model.capacity
        self.num_vehicles = self.model.num_vehicles
        self.family_assignment = self.model.family_assignment
        self.required_per_family = self.model.required_per_family
        self.demands = self.model.demands
        self.cost_matrix = self.model.cost_matrix
        
        # Get nodes per family
        self.family_nodes = [[] for _ in range(self.num_families)]
        for node in range(1, self.num_nodes):  # Skip depot (node 0)
            family = self.family_assignment[node]
            self.family_nodes[family].append(node)
        
        # Best solution found
        self.best_solution = None
        self.best_cost = float('inf')
    
    def distance(self, node1, node2):
        """Calculate distance between two nodes"""
        return self.cost_matrix[node1][node2]
    
    def total_distance(self, routes):
        """Calculate total distance of all routes"""
        total = 0
        for route in routes:
            if not route:
                continue
            # Add distance from depot to first node
            total += self.distance(0, route[0])
            # Add distances between consecutive nodes
            for i in range(len(route) - 1):
                total += self.distance(route[i], route[i + 1])
            # Add distance from last node to depot
            total += self.distance(route[-1], 0)
        return total
    
    def solution_to_string(self, routes):
        """Convert solution to required string format"""
        output = f"{len(routes)}\n"
        for i, route in enumerate(routes):
            if not route:
                continue
            route_str = f"Route {i+1}: 0 "
            for node in route:
                route_str += f"{node} "
            route_str += "0"
            output += route_str + "\n"
        return output
    
    def save_solution(self, routes, filename="solution.txt"):
        """Save solution to file"""
        solution_str = self.solution_to_string(routes)
        with open(filename, 'w') as f:
            f.write(solution_str)
        print(f"Solution saved to {filename}")
    
    def select_nodes_from_families(self):
        """
        Select the required number of nodes from each family.
        For our initial algorithm, we'll select nodes that are closest to the depot.
        """
        selected_nodes = []
        
        for family_idx in range(self.num_families):
            # Get available nodes for this family
            available_nodes = self.family_nodes[family_idx]
            # Number of nodes to select
            to_select = self.required_per_family[family_idx]
            
            # Sort nodes by distance from depot
            sorted_nodes = sorted(available_nodes, key=lambda x: self.distance(0, x))
            
            # Select the closest nodes
            chosen_nodes = sorted_nodes[:to_select]
            selected_nodes.extend(chosen_nodes)
            
        return selected_nodes
    
    def greedy_initial_solution(self):
        """
        Generate initial solution using a greedy approach:
        1. Select the required nodes from each family (closest to depot)
        2. Assign nodes to vehicles one by one using nearest neighbor
        """
        # Select nodes from families
        selected_nodes = self.select_nodes_from_families()
        
        # Initialize routes
        routes = [[] for _ in range(self.num_vehicles)]
        route_loads = [0] * self.num_vehicles
        
        # Sort nodes by distance from depot
        nodes_sorted = sorted(selected_nodes, key=lambda x: self.distance(0, x))
        
        # Assign nodes to vehicles
        for node in nodes_sorted:
            node_demand = self.demands[self.family_assignment[node]]
            
            # Find the best route to insert this node
            best_route = 0
            min_increase = float('inf')
            
            for route_idx in range(self.num_vehicles):
                # Check if capacity constraint is satisfied
                if route_loads[route_idx] + node_demand <= self.capacity:
                    # Calculate cost increase if node is added to this route
                    if not routes[route_idx]:
                        # If route is empty, cost increase is depot->node->depot
                        increase = self.distance(0, node) + self.distance(node, 0)
                    else:
                        # Find best position to insert node
                        best_pos_increase = float('inf')
                        
                        # Try inserting at the beginning
                        pos_increase = self.distance(0, node) + self.distance(node, routes[route_idx][0]) - self.distance(0, routes[route_idx][0])
                        if pos_increase < best_pos_increase:
                            best_pos_increase = pos_increase
                        
                        # Try inserting at the end
                        pos_increase = self.distance(routes[route_idx][-1], node) + self.distance(node, 0) - self.distance(routes[route_idx][-1], 0)
                        if pos_increase < best_pos_increase:
                            best_pos_increase = pos_increase
                        
                        # Try inserting between each pair of nodes
                        for i in range(len(routes[route_idx]) - 1):
                            pos_increase = self.distance(routes[route_idx][i], node) + self.distance(node, routes[route_idx][i+1]) - self.distance(routes[route_idx][i], routes[route_idx][i+1])
                            if pos_increase < best_pos_increase:
                                best_pos_increase = pos_increase
                        
                        increase = best_pos_increase
                    
                    if increase < min_increase:
                        min_increase = increase
                        best_route = route_idx
            
            # Add node to the best route
            if not routes[best_route]:
                routes[best_route].append(node)
            else:
                # Find best position to insert
                best_pos = 0
                best_pos_increase = float('inf')
                
                # Try inserting at the beginning
                pos_increase = self.distance(0, node) + self.distance(node, routes[best_route][0]) - self.distance(0, routes[best_route][0])
                if pos_increase < best_pos_increase:
                    best_pos_increase = pos_increase
                    best_pos = 0
                
                # Try inserting at the end
                pos_increase = self.distance(routes[best_route][-1], node) + self.distance(node, 0) - self.distance(routes[best_route][-1], 0)
                if pos_increase < best_pos_increase:
                    best_pos_increase = pos_increase
                    best_pos = len(routes[best_route])
                
                # Try inserting between each pair of nodes
                for i in range(len(routes[best_route]) - 1):
                    pos_increase = self.distance(routes[best_route][i], node) + self.distance(node, routes[best_route][i+1]) - self.distance(routes[best_route][i], routes[best_route][i+1])
                    if pos_increase < best_pos_increase:
                        best_pos_increase = pos_increase
                        best_pos = i + 1
                
                routes[best_route].insert(best_pos, node)
            
            # Update route load
            route_loads[best_route] += node_demand
        
        return routes
    
    def two_opt_improve(self, routes):
        """
        Improve the routes using 2-opt algorithm.
        This will eliminate route crossings.
        """
        improved = True
        iterations = 0
        max_iterations = 100  # Limit iterations to avoid excessive computation
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for route_idx, route in enumerate(routes):
                if len(route) < 3:  # Need at least 3 nodes for 2-opt
                    continue
                
                route_improved = True
                route_iterations = 0
                max_route_iterations = 20  # Limit per-route iterations
                
                # Keep improving this route as long as possible
                while route_improved and route_iterations < max_route_iterations:
                    route_improved = False
                    route_iterations += 1
                    
                    # Try all possible 2-opt swaps
                    for i in range(len(route) - 1):
                        for j in range(i + 2, len(route)):
                            # Calculate current cost
                            current_cost = 0
                            if i > 0:
                                current_cost += self.distance(route[i-1], route[i])
                            else:
                                current_cost += self.distance(0, route[i])
                            
                            current_cost += self.distance(route[j], route[j+1]) if j < len(route) - 1 else self.distance(route[j], 0)
                            
                            # Calculate cost after 2-opt swap
                            new_cost = 0
                            if i > 0:
                                new_cost += self.distance(route[i-1], route[j])
                            else:
                                new_cost += self.distance(0, route[j])
                            
                            new_cost += self.distance(route[i], route[j+1]) if j < len(route) - 1 else self.distance(route[i], 0)
                            
                            # If better, do the swap
                            if new_cost < current_cost:
                                # Reverse the segment between i and j
                                routes[route_idx][i:j+1] = reversed(routes[route_idx][i:j+1])
                                route_improved = True
                                improved = True
                                break
                        
                        if route_improved:
                            break
        
        return routes
    
    def swap_nodes(self, routes, max_swaps=100):
        """
        Improve solution by swapping nodes between routes.
        This keeps the family constraints intact since we swap nodes from the same family.
        """
        for _ in range(max_swaps):
            # Randomly select two routes
            route_indices = [i for i, route in enumerate(routes) if route]
            if len(route_indices) < 2:
                break
                
            route1_idx, route2_idx = random.sample(route_indices, 2)
            
            # Try to find nodes from the same family
            found_swap = False
            for node1_idx, node1 in enumerate(routes[route1_idx]):
                family1 = self.family_assignment[node1]
                
                for node2_idx, node2 in enumerate(routes[route2_idx]):
                    family2 = self.family_assignment[node2]
                    
                    # If nodes are from the same family, try swapping
                    if family1 == family2:
                        # Check capacity constraints
                        demand1 = self.demands[family1]
                        
                        # Calculate current route loads
                        route1_load = sum(self.demands[self.family_assignment[n]] for n in routes[route1_idx])
                        route2_load = sum(self.demands[self.family_assignment[n]] for n in routes[route2_idx])
                        
                        # Calculate new loads after swap (demand1 == demand2 since same family)
                        # Since we're swapping nodes with the same demand, loads don't actually change
                        
                        # Calculate change in cost
                        old_cost = 0
                        new_cost = 0
                        
                        # Old cost for route 1
                        if node1_idx == 0:
                            old_cost += self.distance(0, node1)
                        else:
                            old_cost += self.distance(routes[route1_idx][node1_idx-1], node1)
                        
                        if node1_idx == len(routes[route1_idx]) - 1:
                            old_cost += self.distance(node1, 0)
                        else:
                            old_cost += self.distance(node1, routes[route1_idx][node1_idx+1])
                        
                        # Old cost for route 2
                        if node2_idx == 0:
                            old_cost += self.distance(0, node2)
                        else:
                            old_cost += self.distance(routes[route2_idx][node2_idx-1], node2)
                        
                        if node2_idx == len(routes[route2_idx]) - 1:
                            old_cost += self.distance(node2, 0)
                        else:
                            old_cost += self.distance(node2, routes[route2_idx][node2_idx+1])
                        
                        # New cost for route 1 (with node2)
                        if node1_idx == 0:
                            new_cost += self.distance(0, node2)
                        else:
                            new_cost += self.distance(routes[route1_idx][node1_idx-1], node2)
                        
                        if node1_idx == len(routes[route1_idx]) - 1:
                            new_cost += self.distance(node2, 0)
                        else:
                            new_cost += self.distance(node2, routes[route1_idx][node1_idx+1])
                        
                        # New cost for route 2 (with node1)
                        if node2_idx == 0:
                            new_cost += self.distance(0, node1)
                        else:
                            new_cost += self.distance(routes[route2_idx][node2_idx-1], node1)
                        
                        if node2_idx == len(routes[route2_idx]) - 1:
                            new_cost += self.distance(node1, 0)
                        else:
                            new_cost += self.distance(node1, routes[route2_idx][node2_idx+1])
                        
                        # If improvement, do the swap
                        if new_cost < old_cost:
                            routes[route1_idx][node1_idx], routes[route2_idx][node2_idx] = routes[route2_idx][node2_idx], routes[route1_idx][node1_idx]
                            found_swap = True
                            break
                
                if found_swap:
                    break
        
        return routes
    
    def swap_with_unselected(self, routes, max_swaps=100):
        """
        Try to improve solution by swapping nodes with unselected nodes from the same family.
        """
        # Get all nodes currently in the solution
        selected_nodes = [node for route in routes for node in route]
        
        for _ in range(max_swaps):
            # Randomly select a route
            route_indices = [i for i, route in enumerate(routes) if route]
            if not route_indices:
                break
                
            route_idx = random.choice(route_indices)
            
            # Randomly select a node in the route
            node_idx = random.randint(0, len(routes[route_idx]) - 1)
            current_node = routes[route_idx][node_idx]
            family = self.family_assignment[current_node]
            
            # Find unselected nodes from the same family
            unselected = [node for node in self.family_nodes[family] if node not in selected_nodes]
            if not unselected:
                continue
            
            # Try each unselected node
            for new_node in unselected:
                # Calculate change in cost
                old_cost = 0
                new_cost = 0
                
                # Old cost with current node
                if node_idx == 0:
                    old_cost += self.distance(0, current_node)
                else:
                    old_cost += self.distance(routes[route_idx][node_idx-1], current_node)
                
                if node_idx == len(routes[route_idx]) - 1:
                    old_cost += self.distance(current_node, 0)
                else:
                    old_cost += self.distance(current_node, routes[route_idx][node_idx+1])
                
                # New cost with new node
                if node_idx == 0:
                    new_cost += self.distance(0, new_node)
                else:
                    new_cost += self.distance(routes[route_idx][node_idx-1], new_node)
                
                if node_idx == len(routes[route_idx]) - 1:
                    new_cost += self.distance(new_node, 0)
                else:
                    new_cost += self.distance(new_node, routes[route_idx][node_idx+1])
                
                # If better, swap nodes
                if new_cost < old_cost:
                    routes[route_idx][node_idx] = new_node
                    selected_nodes.remove(current_node)
                    selected_nodes.append(new_node)
                    break
        
        return routes
    
    def local_search(self, initial_solution, max_iterations=1000, max_non_improving=200):
        """
        Local search to improve the initial solution
        """
        current_solution = [route[:] for route in initial_solution]
        current_cost = self.total_distance(current_solution)
        
        best_solution = [route[:] for route in current_solution]
        best_cost = current_cost
        
        print(f"Starting local search with initial cost: {current_cost}")
        
        non_improving = 0
        for iteration in range(max_iterations):
            # First, apply 2-opt to each route
            improved_solution = self.two_opt_improve([route[:] for route in current_solution])
            
            # Then, try to swap nodes between routes
            improved_solution = self.swap_nodes(improved_solution)
            
            # Finally, try to swap with unselected nodes
            improved_solution = self.swap_with_unselected(improved_solution)
            
            # Calculate new cost
            new_cost = self.total_distance(improved_solution)
            
            # Update if improved
            if new_cost < current_cost:
                current_solution = [route[:] for route in improved_solution]
                current_cost = new_cost
                non_improving = 0
                
                # Update best solution if improved
                if current_cost < best_cost:
                    best_solution = [route[:] for route in current_solution]
                    best_cost = current_cost
                    print(f"Iteration {iteration}: New best solution found with cost {best_cost}")
            else:
                non_improving += 1
                
            # Stop if no improvement for a while
            if non_improving >= max_non_improving:
                print(f"Stopping after {non_improving} non-improving iterations")
                break
            
            # Print progress occasionally
            if iteration % 100 == 0:
                print(f"Iteration {iteration}: Current cost: {current_cost}, Best cost: {best_cost}")
        
        return best_solution, best_cost
    
    def solve(self):
        """Solve the F-CVRP problem"""
        start_time = time.time()
        
        print("Generating initial solution using greedy algorithm...")
        initial_solution = self.greedy_initial_solution()
        initial_cost = self.total_distance(initial_solution)
        print(f"Initial solution cost: {initial_cost}")
        
        # Check if initial solution is valid
        validator = SolutionValidator(self.model, initial_solution)
        if validator.validate():
            print("Initial solution is valid.")
        else:
            print("Initial solution is invalid!")
            return None
        
        print("Improving solution using local search...")
        improved_solution, improved_cost = self.local_search(
            initial_solution,
            max_iterations=1000,
            max_non_improving=200
        )
        
        print(f"Final solution cost: {improved_cost}")
        print(f"Improvement: {initial_cost - improved_cost} ({(initial_cost - improved_cost) / initial_cost * 100:.2f}%)")
        
        # Check if improved solution is valid
        validator = SolutionValidator(self.model, improved_solution)
        if validator.validate():
            print("Final solution is valid.")
            self.best_solution = improved_solution
            self.best_cost = improved_cost
            self.save_solution(improved_solution)
        else:
            print("Final solution is invalid!")
            return None
        
        end_time = time.time()
        print(f"Total execution time: {end_time - start_time:.2f} seconds")
        
        return improved_solution

if __name__ == "__main__":
    fcvrp = FCVRP()
    solution = fcvrp.solve()
