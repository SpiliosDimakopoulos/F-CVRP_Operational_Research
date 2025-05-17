# Family Capacitated Vehicle Routing Problem (F-CVRP) Solver

Hey there! 👋 This is our solution for the F-CVRP problem we worked on for our Operations Research course. We tried to make it as efficient as possible while keeping it easy to understand.

## What's This All About?

So, we had this cool problem to solve: imagine you're running a delivery service, but with a twist! Your customers are organized into "families" (like neighborhoods or groups), and you need to visit a specific number of customers from each family. Oh, and your delivery trucks have limited space, so you can't overload them!

## How We Solved It

We broke this down into two main parts:

1. **First Try (Initial Solution)**
   - We start by picking customers that are close to each other
   - Make sure we don't overload the trucks
   - Check that we visit enough customers from each family

2. **Making It Better (Local Search)**
   - We look at our routes and try to make them shorter
   - Sometimes we reverse parts of the route to see if it helps
   - Keep checking that we're still following all the rules

## The Code Files

- `main.py` - The entry point of our program that shows all the results
- `Solution.py` - Contains our solution algorithm and local search improvements
- `initial_solution.py` - Creates our first attempt at solving the problem
- `Parser.py` - Reads the problem data from files
- `SolutionValidator.py` - Makes sure our solution follows all the rules

## How to Run It

Just open your terminal and type:
```bash
python main.py
```

That's it! The program will:
1. Read the problem from `fcvrp_P-n101-k4_10_3_3.txt`
2. Generate and improve the solution
3. Save it to `solution_example.txt`
4. Show you all the details about the routes, costs, and family visits

## What We Learned

- Making good initial solutions is super important!
- Sometimes the simplest improvements can make a big difference
- It's really satisfying when you find a better route 😊
- Having a clear main program (`main.py`) makes it easier to understand what's happening

## The Team

We're three students who worked together on this:
- Spilios Dimakopoulos
- Giorgos Sarakis
- Giannis Ferentinos

## Notes

- The program usually finds a pretty good solution, but it might not be the absolute best
- It runs in under 5 minutes on a normal computer

### Solution Approach
1. Initial Solution Generation (Nearest Neighbor)
   - Instead of pure randomness, select customers closest to the current route
   - Respect vehicle capacity constraints
   - Satisfy family visit requirements

2. Local Search Improvement (2-opt)
   - local search technique
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

### Limitations
- Heuristic approach, not guaranteed to find the optimal solution
- Performance depends on the specific problem instance
- Limited by computational complexity
