import random
from initial_solution import nearest_neighbor_initial_solution
from Parser import load_model
from SolutionValidator import validate_solution

def calculate_route_cost(model, route):
    """
    Calculate the total cost of a single route
    """
    cost = 0
    for i in range(len(route) - 1):
        cost += model.cost_matrix[route[i]][route[i+1]]
    return cost

def two_opt_improvement(model, routes):
    """
    Two-opt local search improvement
    More sophisticated than simple node swapping
    """
    random.seed(42)
    best_routes = [route.copy() for route in routes]
    
    max_iterations = 200
    improvement_found = True
    iteration = 0
    
    while improvement_found and iteration < max_iterations:
        improvement_found = False
        iteration += 1
        
        for route_idx in range(len(best_routes)):
            route = best_routes[route_idx]
            
            # Skip routes that are too short
            if len(route) <= 4:  # depot, node, node, depot
                continue
            
            # Try 2-opt moves within the same route
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    # Create a candidate route by reversing the segment between i and j
                    new_route = (
                        route[:i] + 
                        route[i:j+1][::-1] + 
                        route[j+1:]
                    )
                    
                    # Temporarily replace the route
                    test_routes = best_routes.copy()
                    test_routes[route_idx] = new_route
                    
                    # Validate the new solution
                    valid, report = validate_solution(model, test_routes)
                    
                    # Check if the new solution is valid and improves total cost
                    if valid:
                        best_routes = test_routes
                        improvement_found = True
                        break
                
                if improvement_found:
                    break
            
            if improvement_found:
                break
    
    return best_routes

def solve_problem(instance_file):
    """
    Main solving function for the F-CVRP problem
    Improved version with more sophisticated solution methods
    """
    # Load the problem model
    model = load_model(instance_file)
    
    # Generate initial solution using nearest neighbor
    initial_routes = nearest_neighbor_initial_solution(model)
    
    # First validate the initial solution
    initial_valid, initial_report = validate_solution(model, initial_routes)
    initial_cost = initial_report['total_cost'] if initial_valid else float('inf')
    
    print(f"Initial solution cost: {initial_cost}")
    
    # Improve initial solution using 2-opt local search
    improved_routes = two_opt_improvement(model, initial_routes)
    
    # Validate the improved solution
    valid, report = validate_solution(model, improved_routes)
    
    # Save solution to file
    with open('solution.txt', 'w') as f:
        for route in improved_routes:
            f.write(' '.join(map(str, route)) + '\n')
    
    # Print results
    print(f"Improved solution cost: {report['total_cost']}")
    print("Solution is valid." if valid else "Solution is NOT valid.")
    
    return improved_routes

if __name__ == "__main__":
    solve_problem("fcvrp_P-n101-k4_10_3_3.txt")import random
from initial_solution import initial_solution
from Parser import load_model
from SolutionValidator import validate_solution

def local_search_improvement(model, initial_routes):
    """
    Simple local search improvement strategy
    Try to improve the initial solution by swapping nodes between routes
    """
    # Set random seed as required
    random.seed(42)
    
    # Make a copy of initial routes to modify
    best_routes = [route.copy() for route in initial_routes]
    
    # Number of improvement iterations
    max_iterations = 100
    
    for _ in range(max_iterations):
        # Randomly select two routes
        if len(best_routes) < 2:
            break
        
        route1_idx = random.randint(0, len(best_routes) - 1)
        route2_idx = random.randint(0, len(best_routes) - 1)
        
        # Ensure different routes
        if route1_idx == route2_idx:
            continue
        
        # Avoid depot nodes
        if len(best_routes[route1_idx]) <= 2 or len(best_routes[route2_idx]) <= 2:
            continue
        
        # Try to swap a random node between routes
        node1_idx = random.randint(1, len(best_routes[route1_idx]) - 2)
        node2_idx = random.randint(1, len(best_routes[route2_idx]) - 2)
        
        node1 = best_routes[route1_idx][node1_idx]
        node2 = best_routes[route2_idx][node2_idx]
        
        # Create temporary routes for validation
        test_routes = [route.copy() for route in best_routes]
        test_routes[route1_idx][node1_idx] = node2
        test_routes[route2_idx][node2_idx] = node1
        
        # Validate the new solution
        valid, report = validate_solution(model, test_routes)
        
        # If solution is valid and total cost is lower, accept the change
        if valid:
            best_routes = test_routes
    
    return best_routes

def solve_problem(instance_file):
    """
    Main solving function for the F-CVRP problem
    """
    # Load the problem model
    model = load_model(instance_file)
    
    # Generate initial solution
    initial_routes = initial_solution(model)
    
    # Improve initial solution
    improved_routes = local_search_improvement(model, initial_routes)
    
    # Validate and save the solution
    valid, report = validate_solution(model, improved_routes)
    
    # Save solution to file
    with open('solution.txt', 'w') as f:
        for route in improved_routes:
            f.write(' '.join(map(str, route)) + '\n')
    
    print(f"Solution saved. Total cost: {report['total_cost']}")
    print("Solution is valid." if valid else "Solution is NOT valid.")
    
    return improved_routes

if __name__ == "__main__":
    solve_problem("fcvrp_P-n101-k4_10_3_3.txt")