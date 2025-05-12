import random
import math
from Parser import load_model

def nearest_neighbor_initial_solution(model):
    """
    Create an initial solution using a simple nearest neighbor approach
    This is slightly more intelligent than pure randomness
    """
    # Initialize random generators with the allowed seed
    random.seed(42)
    
    # List of all customers
    customers = model.customers.copy()
    
    # Track visits to each family
    family_visits = [0] * model.num_fam
    
    # Routes to return
    routes = []
    
    # For each vehicle
    for _ in range(model.vehicles):
        route = [0]  # Start from depot
        current_load = 0
        current_position = 0  # Start at depot
        
        # Try to fill the route
        while customers and len(route) < 30:  # Limit to prevent infinite loop
            # Find the nearest feasible customer
            best_candidate = None
            min_distance = float('inf')
            
            for candidate in customers:
                # Check feasibility conditions
                if (current_load + candidate.demand <= model.capacity and 
                    family_visits[candidate.family] < model.families[candidate.family].required_visits):
                    
                    # Calculate distance
                    distance = model.cost_matrix[current_position][candidate.id]
                    
                    # Choose the nearest feasible customer
                    if distance < min_distance:
                        min_distance = distance
                        best_candidate = candidate
            
            # If no feasible customer found, end this route
            if best_candidate is None:
                route.append(0)  # Return to depot
                routes.append(route)
                break
            
            # Add the best candidate to the route
            route.append(best_candidate.id)
            current_load += best_candidate.demand
            family_visits[best_candidate.family] += 1
            current_position = best_candidate.id
            
            # Remove the customer from available customers
            customers.remove(best_candidate)
            
            # If route is getting too long or no more customers
            if len(route) > 1 and (not customers or current_load >= model.capacity):
                route.append(0)  # Return to depot
                routes.append(route)
                break
    
    # Handle any remaining customers in additional routes
    while customers:
        route = [0]
        current_load = 0
        current_position = 0
        
        while customers and len(route) < 30:
            best_candidate = None
            min_distance = float('inf')
            
            for candidate in customers:
                if (current_load + candidate.demand <= model.capacity and 
                    family_visits[candidate.family] < model.families[candidate.family].required_visits):
                    
                    distance = model.cost_matrix[current_position][candidate.id]
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_candidate = candidate
            
            if best_candidate is None:
                route.append(0)
                routes.append(route)
                break
            
            route.append(best_candidate.id)
            current_load += best_candidate.demand
            family_visits[best_candidate.family] += 1
            current_position = best_candidate.id
            
            customers.remove(best_candidate)
            
            if len(route) > 1 and (not customers or current_load >= model.capacity):
                route.append(0)
                routes.append(route)
                break
    
    return routesimport random
import math
from Parser import load_model

def initial_solution(model):
    """
    Create an initial feasible solution for the F-CVRP problem
    Using a simple heuristic approach
    """
    # Initialize random generators with one of the allowed seeds
    random.seed(42)
    
    # List of all customers
    customers = model.customers.copy()
    
    # Track visits to each family
    family_visits = [0] * model.num_fam
    
    # Routes to return
    routes = []
    
    # For each vehicle
    for _ in range(model.vehicles):
        route = [0]  # Start from depot
        current_load = 0
        
        # Try to fill the route
        while customers and len(route) < 30:  # Limit to prevent infinite loop
            # Randomly select a customer
            candidate = random.choice(customers)
            
            # Check if we can add the customer
            if (current_load + candidate.demand <= model.capacity and 
                family_visits[candidate.family] < model.families[candidate.family].required_visits):
                
                route.append(candidate.id)
                current_load += candidate.demand
                family_visits[candidate.family] += 1
                
                # Remove the customer
                customers.remove(candidate)
            
            # If we can't add more customers
            if len(route) > 1 and (not customers or current_load >= model.capacity):
                route.append(0)  # Return to depot
                routes.append(route)
                break
    
    # If there are remaining unassigned customers
    while customers:
        # Create a new route for remaining customers
        route = [0]
        current_load = 0
        
        # Try to add remaining customers
        while customers and len(route) < 30:
            candidate = random.choice(customers)
            
            if (current_load + candidate.demand <= model.capacity and 
                family_visits[candidate.family] < model.families[candidate.family].required_visits):
                
                route.append(candidate.id)
                current_load += candidate.demand
                family_visits[candidate.family] += 1
                
                customers.remove(candidate)
            
            # If we can't add more customers
            if len(route) > 1 and (not customers or current_load >= model.capacity):
                route.append(0)  # Return to depot
                routes.append(route)
                break
    
    return routes