
import math
from pysat.solvers import Glucose3

def generate_variables(n):
    return [
        [i * n + j + 1 for j in range(n)]
        for i in range(n)
    ]


def generate_new_variables(next_var, length):
    if length <= 1:
        return [], next_var

    num_aux = math.ceil(math.log2(length))
    aux_vars = list(range(next_var, next_var + num_aux))

    return aux_vars, next_var + num_aux


def binary_encoding(clauses, target, aux_vars, index):
    for bit_index, aux in enumerate(aux_vars):
        bit = (index >> bit_index) & 1

        if bit == 1:
            clauses.append([-target, aux])
        else:
            clauses.append([-target, -aux])


def at_most_one(clauses, variables, next_var):
    if len(variables) <= 1:
        return next_var

    aux_vars, next_var = generate_new_variables(
        next_var, len(variables)
    )

    for index, var in enumerate(variables):
        binary_encoding(clauses, var, aux_vars, index)

    return next_var


def exactly_one(clauses, variables, next_var):
    """Exactly One = At Least One + At Most One."""
    clauses.append(list(variables))
    return at_most_one(clauses, variables, next_var)


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

    diagonals = {}

    anti_diagonals = {}

    for i in range(n):
        for j in range(n):
            var = variables[i][j]

            diagonals.setdefault(i - j, []).append(var)
            anti_diagonals.setdefault(i + j, []).append(var)

    for diagonal in diagonals.values():
        next_var = at_most_one(
            clauses, diagonal, next_var
        )

    for diagonal in anti_diagonals.values():
        next_var = at_most_one(
            clauses, diagonal, next_var
        )

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

    finally:
        solver.delete()


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
