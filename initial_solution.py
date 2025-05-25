# initial_solution.py
# This file creates the first solution for our vehicle routing problem
# We use a savings-based approach to build good initial routes

import random
from Parser import load_model

# Calculate how much we save by connecting two customers
def calculate_savings(model, i, j):
    return model.cost_matrix[0][i] + model.cost_matrix[0][j] - model.cost_matrix[i][j]

# Main function to create our first solution
def initial_solution(model):
    # Set random seed for consistent results
    random.seed(42)
    
    # Make a copy of all customers
    customers = model.customers.copy()
    
    # Keep track of how many times we visit each family
    family_visits = [0] * model.num_fam
    family_requirements = [family.required_visits for family in model.families]
    
    # Figure out which families are most important
    family_priorities = []
    for i, family in enumerate(model.families):
        # Families that need more visits and have higher demand get higher priority
        priority = (family.required_visits * 2) + (family.demand / model.capacity)
        family_priorities.append(priority)
    
    # Sort customers by family priority and distance from depot
    customers.sort(key=lambda c: (
        -family_priorities[c.family],  # Important families first
        model.cost_matrix[0][c.id]     # Then by distance from depot
    ))
    
    # List to store our routes
    routes = []
    
    # Helper function to find the best customer to add to a route
    def find_best_customer(available_customers, current_load, current_route, family_visits):
        best_candidate = None
        best_score = float('-inf')
        
        # Get the last node in the current route
        last_node = current_route[-1] if current_route else 0
        
        for candidate in available_customers:
            # Skip if adding this customer would make the route too heavy
            if current_load + candidate.demand > model.capacity:
                continue
                
            # Skip if this family already has enough visits
            family_need = family_requirements[candidate.family] - family_visits[candidate.family]
            if family_need <= 0:
                continue
            
            # Calculate how much we save by adding this customer
            savings = calculate_savings(model, last_node, candidate.id)
            
            # Calculate a score based on several factors
            score = (
                savings * 0.4 +                    # How much we save
                family_need * 0.3 +               # How much this family needs visits
                family_priorities[candidate.family] * 0.2 +  # Family importance
                (1 / model.cost_matrix[last_node][candidate.id]) * 0.1  # How close they are
            )
            
            if score > best_score:
                best_candidate = candidate
                best_score = score
        
        return best_candidate
    
    # First try to meet all family requirements
    while any(visits < req for visits, req in zip(family_visits, family_requirements)):
        if len(routes) >= model.vehicles:
            # If we've used all vehicles but still need more visits,
            # try to add customers to existing routes
            for route_idx in range(len(routes)):
                route = routes[route_idx]
                current_load = sum(model.customers[node].demand for node in route[1:-1])
                
                while customers and len(route) < 30:
                    best_candidate = find_best_customer(customers, current_load, route, family_visits)
                    if best_candidate is None:
                        break
                        
                    route.append(best_candidate.id)
                    current_load += best_candidate.demand
                    family_visits[best_candidate.family] += 1
                    customers.remove(best_candidate)
                
                routes[route_idx] = route
            break
            
        # Start a new route
        route = [0]  # Start from depot
        current_load = 0
        
        # Try to fill the route
        while customers and len(route) < 30:
            best_candidate = find_best_customer(customers, current_load, route, family_visits)
            
            # If we can't find a good customer, end this route
            if best_candidate is None:
                break
            
            # Add the customer to the route
            route.append(best_candidate.id)
            current_load += best_candidate.demand
            family_visits[best_candidate.family] += 1
            customers.remove(best_candidate)
        
        # Close the route if it has customers
        if len(route) > 1:
            route.append(0)  # Return to depot
            routes.append(route)
    
    # Try to add any remaining customers if we have space
    while customers and len(routes) < model.vehicles:
        route = [0]
        current_load = 0
        
        while customers and len(route) < 30:
            best_candidate = find_best_customer(customers, current_load, route, family_visits)
            
            if best_candidate is None:
                break
            
            route.append(best_candidate.id)
            current_load += best_candidate.demand
            family_visits[best_candidate.family] += 1
            customers.remove(best_candidate)
        
        if len(route) > 1:
            route.append(0)
            routes.append(route)
    
    # Try to improve each route by reordering customers
    for i in range(len(routes)):
        route = routes[i]
        if len(route) <= 4:  # Skip very short routes
            continue
            
        improved = True
        while improved:
            improved = False
            for j in range(1, len(route) - 2):
                for k in range(j + 2, len(route) - 1):
                    # Try reversing part of the route
                    new_route = route[:j] + route[j:k+1][::-1] + route[k+1:]
                    
                    # Check if this makes the route better
                    old_cost = sum(model.cost_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
                    new_cost = sum(model.cost_matrix[new_route[i]][new_route[i+1]] for i in range(len(new_route)-1))
                    
                    if new_cost < old_cost:
                        routes[i] = new_route
                        route = new_route
                        improved = True
                        break
                if improved:
                    break
    
    return routes