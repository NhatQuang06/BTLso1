import math
import time
from pysat.solvers import Glucose3


def generate_variables(n):
    return [
        [i * n + j + 1 for j in range(n)]
        for i in range(n)
    ]


def at_most_one_pairwise(clauses, variables):
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])


def exactly_one_pairwise(clauses, variables):
    clauses.append(list(variables))
    at_most_one_pairwise(clauses, variables)


def grouping_variables(variables, group_size):
    return [
        variables[i:i + group_size]
        for i in range(0, len(variables), group_size)
    ]


def commander_amo(clauses, variables, next_var):
    if len(variables) <= 1:
        return next_var

    # Small groups reduce overhead; group size is configurable.
    group_size = min(4, len(variables))
    groups = grouping_variables(variables, group_size)

    commanders = list(
        range(next_var, next_var + len(groups))
    )
    next_var += len(groups)

    # AMO between all commanders
    at_most_one_pairwise(clauses, commanders)

    for group, commander in zip(groups, commanders):
        # At most one input variable inside each group
        at_most_one_pairwise(clauses, group)

        # If any input is true, its commander must be true:
        # x -> c, encoded as (not x OR c)
        for x in group:
            clauses.append([-x, commander])

        # If the commander is true, at least one group
        # member must be true:
        # c -> (x1 OR x2 OR ...)
        clauses.append([-commander] + group)

    return next_var


def generate_clauses(n, variables):
    clauses = []
    next_var = n * n + 1

    # Exactly one queen per row
    for row in variables:
        exactly_one_pairwise(clauses, row)

    # Exactly one queen per column
    for col in range(n):
        column = [variables[row][col] for row in range(n)]
        exactly_one_pairwise(clauses, column)

    # At most one queen per diagonal
    for diff in range(-(n - 1), n):
        diagonal = [
            variables[i][j]
            for i in range(n)
            for j in range(n)
            if i - j == diff
        ]
        next_var = commander_amo(clauses, diagonal, next_var)

    for total in range(2 * n - 1):
        diagonal = [
            variables[i][j]
            for i in range(n)
            for j in range(n)
            if i + j == total
        ]
        next_var = commander_amo(clauses, diagonal, next_var)

    return clauses, next_var - 1


def solve_n_queens(n):
    if n < 1:
        raise ValueError("n must be >= 1")

    variables = generate_variables(n)
    clauses, total_variables = generate_clauses(n, variables)

    start = time.perf_counter()

    with Glucose3(bootstrap_with=clauses) as solver:
        status = solver.solve()
        model = solver.get_model() if status else None

    elapsed = time.perf_counter() - start

    if model is None:
        return None, elapsed, total_variables, len(clauses)

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

    return solution, elapsed, total_variables, len(clauses)


def print_solution(solution):
    if solution is None:
        print("No solution found.")
        return

    for row in solution:
        print(" ".join("Q" if cell else "." for cell in row))


if __name__ == "__main__":
    n = int(input("Nhap N: "))

    solution, elapsed, num_vars, num_clauses = solve_n_queens(n)

    print("Status:", "SAT" if solution is not None else "UNSAT")
    print(f"Elapsed time: {elapsed:.6f} seconds")
    print("Variables:", num_vars)
    print("Clauses:", num_clauses)

    print_solution(solution)