# Family Capacitated Vehicle Routing Problem (F-CVRP) Solver

## Project Overview
An improved solver for the Family Capacitated Vehicle Routing Problem (F-CVRP) that uses more sophisticated solution strategies.

### Solution Approach
1. Initial Solution Generation (Nearest Neighbor)
   - Instead of pure randomness, select customers closest to the current route
   - Respect vehicle capacity constraints
   - Satisfy family visit requirements

2. Local Search Improvement (2-opt)
   - Advanced local search technique
   - Attempts to improve routes by reversing route segments
   - Validates each potential improvement

### Solution Methods
- **Initial Solution**: Nearest Neighbor Algorithm
  - Selects customers based on proximity
  - Considers capacity and family visit constraints

- **Improvement**: 2-opt Local Search
  - Explores route modifications
  - Attempts to reduce total route distance

### Files
- `Solution.py`: Main solving script
- `initial_solution.py`: Initial solution generation
- `Parser.py`: Problem instance parsing
- `SolutionValidator.py`: Solution validation

### How to Run
```bash

# Run the solver
python Solution.py
```

### Performance
- Uses a fixed random seed (42) for reproducibility
- Designed to find a good (but not necessarily optimal) solution
- Typically provides a reasonably efficient route plan

### Limitations
- Heuristic approach, not guaranteed to find the optimal solution
- Performance depends on the specific problem instance
- Limited by computational complexity

### Requirements
- Python 3.7+
- Tested with the provided F-CVRP instance file

### Contributors
- Spilios Dimakopoulos
- Giorgos Sarakis
- Giannis Ferentinos