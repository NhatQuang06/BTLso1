from pysat.solvers import Glucose3

new_variables_count = 0
def generate_variables(n):
    return [[i * n + j + 1 for j in range(n)] for i in range(n)]


def generate_new_variables(n, length):
    global new_variables_count

    # Sequential Counter can be skipped for 0 or 1 input
    if length <= 1:
        return []
    
    start = n * n + new_variables_count
    count = length - 1

    result = list(range(start + 1, start + count + 1))
    new_variables_count += count

    return result


def at_most_one(clauses, variables, n):
    if len(variables) <= 1:
        return

    aux = generate_new_variables(n, len(variables))

    # First input implies the first auxiliary variable
    clauses.append([-variables[0], aux[0]])

    for i in range(1, len(variables) - 1):
        # If input i is true, auxiliary i must be true
        clauses.append([-variables[i], aux[i]])

        # Propagate the sequential counter
        clauses.append([-aux[i - 1], aux[i]])

        # Prevent two inputs from being true
        clauses.append([-aux[i - 1], -variables[i]])

    # The last input cannot be true if a previous one was true
    clauses.append([-aux[-1], -variables[-1]])

def exactly_one(clauses, variables, n):
    clauses.append(variables)
    at_most_one(clauses, variables, n)


def generate_clauses(n, variables):
    clauses = []

    # Exactly one queen in each row
    for row in range(n):
        exactly_one(clauses, variables[row], n)

    # Exactly one queen in each column
    for col in range(n):
        column = [variables[row][col] for row in range(n)]
        exactly_one(clauses, column, n)


    # At most one queen in each diagonal
    for diff in range(-(n - 1), n):
        diagonal = [
            variables[i][j]
            for i in range(n)
            for j in range(n)
            if i - j == diff
        ]
        at_most_one(clauses, diagonal, n)

    for total in range(2 * n - 1):
        diagonal = [
            variables[i][j]
            for i in range(n)
            for j in range(n)
            if i + j == total
        ]
        at_most_one(clauses, diagonal, n)


    return clauses


def solve_n_queens(n):
    global new_variables_count

    if n < 1:
        raise ValueError("n must be >= 1")

    new_variables_count = 0

    variables = generate_variables(n)
    clauses = generate_clauses(n, variables)

    with Glucose3(bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None

        model = solver.get_model()

    true_variables = {
        literal for literal in model if literal > 0
    }

    return [
        [
            int(variables[i][j] in true_variables)
            for j in range(n)
        ]
        for i in range(n)
    ]


def print_solution(solution):
    if solution is None:
        print("No solution found.")
    else:
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))

if __name__ == "__main__":
    n = int(input("Nhap N: "))
    solution = solve_n_queens(n)
    print_solution(solution)

