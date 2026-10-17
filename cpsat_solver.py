import time
from ortools.sat.python import cp_model

def solve_nqueens_cpsat(n, timeout_sec=300):
    if n < 1:
        raise ValueError("n must be >= 1")
    model = cp_model.CpModel()
    queens = [
        model.NewIntVar(0, n - 1, f'q_{i}') 
        for i in range(n)
    ]

    model.AddAllDifferent(queens)
    model.AddAllDifferent([queens[i] + i for i in range(n)])
    model.AddAllDifferent([queens[i] - i for i in range(n)])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_sec

    start = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - start

    is_solved = (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE)
    solution = None

    if is_solved:
        solution = [solver.Value(queens[i]) for i in range(n)]

    return is_solved, elapsed, solution, solver.StatusName(status)


if __name__ == "__main__":
    n = int(input("Nhap N: "))

    solved, elapsed, solution, status = solve_nqueens_cpsat(n)

    print("Trang thai:", status)
    print(f"Thoi gian: {elapsed:.6f} giay")

    if solved:
        print("Vi tri cot cua hau:", solution)

        for r in range(n):
            row = [
                "Q" if solution[r] == c else "."
                for c in range(n)
            ]
            print(" ".join(row))
    else:
        print("Khong tim thay nghiem.")