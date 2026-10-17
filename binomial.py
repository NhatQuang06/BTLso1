from pysat.solvers import Glucose3


def generate_variables(n):
    return [
        [i * n + j + 1 for j in range(n)] 
        for i in range(n)
    ]


def at_most_one(clauses, variables):
    for i in range(0, len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])
    return clauses


def exactly_one(clauses, variables):
    clauses.append(variables)
    at_most_one(clauses, variables)


def generate_clauses(n, variables):
    clauses = []

    for i in range(n):
        exactly_one(clauses, variables[i])

    for j in range(n):
        column = [variables[i][j] for i in range(n)]
        exactly_one(clauses, column)


    for i in range(n):
        for j in range(n):
            for k in range(1, n):
                if i + k < n and j + k < n:
                    at_most_one(clauses, [variables[i][j], variables[i + k][j + k]])
                if i + k < n and j - k >= 0:
                    at_most_one(clauses, [variables[i][j], variables[i + k][j - k]])

    return clauses


def solve_n_queens(n):
    if n < 1:
        raise ValueError("n must be >= 1")
    variables = generate_variables(n)
    clauses = generate_clauses(n, variables)

    with Glucose3(bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None

        model = solver.get_model()

    true_variables = {
        literal for literal in model if literal > 0
    }

    solution = [
        [
            int(variables[i][j] in true_variables)
            for j in range(n)
        ]
        for i in range(n)
    ]

    return solution


def print_solution(solution):
    if solution is None:
        print("No solution found.")
    else:
        print(solution)
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))


if __name__ == "__main__":
    n = int(input("Nhap N: "))
    solution = solve_n_queens(n)
    print_solution(solution)