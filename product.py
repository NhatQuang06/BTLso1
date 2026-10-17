
import math
import time
from pysat.solvers import Glucose3


def generate_variables(n):
    return [
        [i * n + j + 1 for j in range(n)]
        for i in range(n)
    ]


def pairwise_amo(clauses, variables):
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            clauses.append([-variables[i], -variables[j]])



def product_amo(clauses, variables, next_var):
    m = len(variables)

    if m <= 1:
        return next_var

    if m <= 4:
        pairwise_amo(clauses, variables)
        return next_var

    p = math.ceil(math.sqrt(m))
    q = math.ceil(m / p)

    row_vars = list(range(next_var, next_var + p))
    next_var += p

    col_vars = list(range(next_var, next_var + q))
    next_var += q

    groups_row = [[] for _ in range(p)]
    groups_col = [[] for _ in range(q)]

    for k, var in enumerate(variables):
        r = k // q
        c = k % q

        groups_row[r].append(var)
        groups_col[c].append(var)

        clauses.append([-var, row_vars[r]])
        clauses.append([-var, col_vars[c]])

    for r in range(p):
        clauses.append(
            [-row_vars[r]] + groups_row[r]
        )

    for c in range(q):
        clauses.append(
            [-col_vars[c]] + groups_col[c]
        )

    next_var = product_amo(clauses, row_vars, next_var)
    next_var = product_amo(clauses, col_vars, next_var)

    return next_var


def exactly_one(clauses, variables, next_var):
    """Exactly One = At Least One + At Most One."""
    if not variables:
        clauses.append([])
        return next_var

    clauses.append(list(variables))

    next_var = product_amo(clauses, variables, next_var)

    return next_var



def generate_clauses(n, variables):
    clauses = []
    next_var = n * n + 1

    for i in range(n):
        next_var = exactly_one(
            clauses, variables[i], next_var
        )

    for j in range(n):
        column = [variables[i][j] for i in range(n)]
        next_var = exactly_one(
            clauses, column, next_var
        )

    descending_diagonals = {}
    ascending_diagonals = {}

    for i in range(n):
        for j in range(n):
            var = variables[i][j]

            descending_diagonals.setdefault(i - j, []).append(var)
            ascending_diagonals.setdefault(i + j, []).append(var)

    for diagonal in descending_diagonals.values():
        if len(diagonal) > 1:
            next_var = product_amo(clauses, diagonal, next_var)

    for diagonal in ascending_diagonals.values():
        if len(diagonal) > 1:
            next_var = product_amo(clauses, diagonal, next_var)

    return clauses, next_var - 1



def solve_n_queens(n):
    if n < 1:
        raise ValueError("n must be >= 1")

    variables = generate_variables(n)
    clauses, num_vars = generate_clauses(n, variables)

    solver = Glucose3()

    try:
        for clause in clauses:
            solver.add_clause(clause)

        if not solver.solve():
            return None

        model = solver.get_model()

        true_vars = {
            literal for literal in model
            if literal > 0
        }

        board = [
            [
                int(variables[i][j] in true_vars)
                for j in range(n)
            ]
            for i in range(n)
        ]

        return board

    finally:
        solver.delete()


if __name__ == "__main__":
    n = int(input("Nhap N: "))
    start = time.perf_counter()
    solution = solve_n_queens(n)
    elapsed = time.perf_counter() - start

    if solution is None:
            print("No solution found.")
    else:
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))

    print(f"Thời gian tổng: {elapsed:.6f} giây")
