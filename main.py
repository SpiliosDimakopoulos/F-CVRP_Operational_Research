# main.py
# This is our main program that runs the vehicle routing problem solver
# It loads the problem data and checks if our solution is good

import os
from Parser import load_model
from SolutionValidator import validate_solution, parse_solution_file
import Solution

# Main function that runs everything
def main(instance_file, solution_file):
    print(f"Instance '{instance_file}'")
    # Load the problem data
    model = load_model(instance_file)

    # Print some information about the problem
    print("\nModel Summary:")
    print(f"Number of nodes: {model.num_nodes}")
    print(f"Number of families: {model.num_fam}")
    print(f"Required visits: {model.num_req}")
    print(f"Vehicle capacity: {model.capacity}")
    print(f"Number of vehicles: {model.vehicles}")

    # Print information about each family
    print("\nFamily information:")
    for i, family in enumerate(model.families):
        print(
            f"Family {i}: {len(family.nodes)} members, {family.required_visits} required visits, demand: {family.demand}")

    # If we have a solution file, check if it's good
    if solution_file:
        # Make sure the solution file exists
        if not os.path.exists(solution_file):
            print(f"Error: Solution file '{solution_file}' does not exist.")
            return

        print(f"\nValidating solution from '{solution_file}'...")
        # Read the routes from the solution file
        routes = parse_solution_file(solution_file)

        # Print each route
        print("\nRoutes:")
        for i, route in enumerate(routes):
            print(f"Route {i}: {route}")

        # Check if the solution is valid
        valid, report = validate_solution(model, routes)

        if valid:
            print("\nSolution is VALID.")
            print(f"Total cost: {report['total_cost']}")
            
            # Print details about each route
            print("\nRoute details:")
            for i, (load, cost) in enumerate(zip(report['route_loads'], report['route_costs'])):
                print(f"Route {i}: Load = {load}/{model.capacity}, Cost = {cost}")

            # Print how many times we visited each family
            print("\nFamily visits:")
            for family_id, visits in report['family_visits'].items():
                family = model.families[family_id]
                print(f"Family {family_id}: {visits}/{family.required_visits} required visits")
        else:
            print("\nSolution is INVALID.")
            print("Errors:")
            for error in report['errors']:
                print(f"- {error}")

# Run the program with our test files
if __name__ == "__main__":
    main("fcvrp_P-n101-k4_10_3_3.txt", "solution_example.txt")