# Solution.py
# This file contains the implementation of our solution for the vehicle routing problem
# We use a simple local search approach with 2-opt moves to improve the initial solution

import random
import time
from initial_solution import initial_solution
from Parser import load_model
from SolutionValidator import validate_solution

# Function to calculate the cost of a single route
def calculate_route_cost(model, route):
    cost = 0
    for i in range(len(route) - 1):
        cost += model.cost_matrix[route[i]][route[i+1]]
    return cost

# Function to calculate the total load of a route
def calculate_route_load(model, route):
    try:
        return sum(model.customers[node].demand for node in route[1:-1] 
                  if 0 <= node < len(model.customers))
    except (IndexError, AttributeError):
        return float('inf')  # Return a very large number for invalid routes

# Function to count how many times each family is visited
def count_family_visits(model, routes):
    family_visits = [0] * model.num_fam
    for route in routes:
        for node in route[1:-1]:  # Skip the depot nodes
            family_visits[model.customers[node].family] += 1
    return family_visits

# Function to calculate the total cost of all routes
def calculate_total_cost(model, routes):
    return sum(calculate_route_cost(model, route) for route in routes)

# Function to check if all family visit requirements are met
def validate_family_requirements(family_visits, family_requirements):
    return all(visits >= req for visits, req in zip(family_visits, family_requirements))

# Function to try a 2-opt move (reversing a segment of the route)
def try_2opt_move(model, route, i, j):
    if i >= j or i == 0 or j == len(route) - 1:
        return None, None
        
    # Create new route by reversing the segment
    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
    
    # Check if the load is still valid
    route_load = calculate_route_load(model, new_route)
    if route_load > model.capacity:
        return None, None
    
    # Calculate cost difference
    old_cost = calculate_route_cost(model, route)
    new_cost = calculate_route_cost(model, new_route)
    
    if new_cost < old_cost:
        return new_route, new_cost - old_cost
    
    return None, None

# Function to merge routes if we have too many
def merge_routes(model, routes):
    if len(routes) <= model.vehicles:
        return routes
        
    # Sort routes by cost and keep the most expensive ones
    routes.sort(key=lambda r: calculate_route_cost(model, r))
    kept_routes = routes[:model.vehicles-1]
    routes_to_merge = routes[model.vehicles-1:]
    
    # Combine all nodes from routes to merge into one route
    merged_route = [0]  # Start with depot
    for route in routes_to_merge:
        merged_route.extend(route[1:-1])  # Add all nodes except depots
    merged_route.append(0)  # End with depot
    
    # Try to improve the merged route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(merged_route) - 2):
            for j in range(i + 2, len(merged_route) - 1):
                new_route, cost_diff = try_2opt_move(model, merged_route, i, j)
                if new_route and cost_diff < 0:
                    merged_route = new_route
                    improved = True
                    break
            if improved:
                break
    
    kept_routes.append(merged_route)
    return kept_routes

# Main local search function
def local_search(model, routes, max_iterations=100):
    best_routes = [route.copy() for route in routes]
    best_cost = calculate_total_cost(model, best_routes)
    family_requirements = [family.required_visits for family in model.families]
    
    iteration = 0
    no_improvement_count = 0
    max_no_improvement = 15  # Stop if no improvement for 15 iterations
    
    while iteration < max_iterations and no_improvement_count < max_no_improvement:
        improved = False
        iteration += 1
        
        # Try to improve each route
        for route_idx in range(len(best_routes)):
            route = best_routes[route_idx]
            
            # Skip very short routes
            if len(route) <= 4:
                continue
            
            # Try 2-opt moves between nearby nodes
            for i in range(1, len(route) - 2):
                for j in range(i + 2, min(i + 7, len(route) - 1)):
                    new_route, cost_diff = try_2opt_move(model, route, i, j)
                    
                    if new_route and cost_diff < 0:
                        # Check if the new route is valid
                        temp_routes = best_routes.copy()
                        temp_routes[route_idx] = new_route
                        new_family_visits = count_family_visits(model, temp_routes)
                        
                        if validate_family_requirements(new_family_visits, family_requirements):
                            best_routes[route_idx] = new_route
                            best_cost += cost_diff
                            improved = True
                            no_improvement_count = 0
                            break
                
                if improved:
                    break
        
        if not improved:
            no_improvement_count += 1
            
        # One last try with full search range before stopping
        if no_improvement_count == max_no_improvement - 1:
            for route_idx in range(len(best_routes)):
                route = best_routes[route_idx]
                if len(route) <= 4:
                    continue
                    
                for i in range(1, len(route) - 2):
                    for j in range(i + 2, len(route) - 1):
                        new_route, cost_diff = try_2opt_move(model, route, i, j)
                        if new_route and cost_diff < 0:
                            temp_routes = best_routes.copy()
                            temp_routes[route_idx] = new_route
                            new_family_visits = count_family_visits(model, temp_routes)
                            if validate_family_requirements(new_family_visits, family_requirements):
                                best_routes[route_idx] = new_route
                                best_cost += cost_diff
                                improved = True
                                no_improvement_count = 0
                                break
                    if improved:
                        break
                if improved:
                    break
    
    return best_routes, best_cost

# Main function to generate and save the solution
def generate_solution(instance_file, solution_file):
    model = load_model(instance_file)
    initial_routes = initial_solution(model)
    
    # Merge routes if needed
    if len(initial_routes) > model.vehicles:
        initial_routes = merge_routes(model, initial_routes)
    
    # Improve solution with local search
    improved_routes, solution_cost = local_search(model, initial_routes)
    
    # Save solution to file
    with open(solution_file, 'w') as f:
        for route in improved_routes:
            f.write(' '.join(map(str, route)) + '\n')
    
    return improved_routes

# Generate solution when the file is run
generate_solution("fcvrp_P-n101-k4_10_3_3.txt", "solution_example.txt")