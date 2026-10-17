
import time
import gurobipy as gp
from gurobipy import GRB


def solve_nqueens_mip(n, timeout_sec=300):
    if n < 1:
        raise ValueError("n must be >= 1")

    model = None
    env = None

    try:
        env = gp.Env(empty=True)
        env.setParam("OutputFlag", 0)
        env.start()

        model = gp.Model("nqueens_mip", env=env)
        model.setParam("TimeLimit", timeout_sec)

        x = model.addVars(
            n, n,
            vtype=GRB.BINARY,
            name="x"
        )

        for i in range(n):
            model.addConstr(
                gp.quicksum(x[i, j] for j in range(n)) == 1
            )

        # Mỗi cột có đúng một quân hậu.
        for j in range(n):
            model.addConstr(
                gp.quicksum(x[i, j] for i in range(n)) == 1
            )

        for k in range(-n + 1, n):
            model.addConstr(
                gp.quicksum(
                    x[i, j]
                    for i in range(n)
                    for j in range(n)
                    if i - j == k
                ) <= 1
            )

        for k in range(2 * n - 1):
            model.addConstr(
                gp.quicksum(
                    x[i, j]
                    for i in range(n)
                    for j in range(n)
                    if i + j == k
                ) <= 1
            )

        start = time.perf_counter()
        model.optimize()
        elapsed = time.perf_counter() - start

        has_solution = model.SolCount > 0

        solution = None
        if has_solution:
            solution = [
                [int(x[i, j].X > 0.5) for j in range(n)]
                for i in range(n)
            ]

        status_names = {
            GRB.OPTIMAL: "OPTIMAL",
            GRB.INFEASIBLE: "INFEASIBLE",
            GRB.TIME_LIMIT: "TIME_LIMIT",
            GRB.INTERRUPTED: "INTERRUPTED",
            GRB.UNBOUNDED: "UNBOUNDED",
        }

        status = status_names.get(
            model.Status,
            f"STATUS_{model.Status}"
        )

        return has_solution, elapsed, solution, status

    except gp.GurobiError as e:
        print(f"Gurobi error: {e}")
        return False, None, None, "ERROR"

    finally:
        if model is not None:
            model.dispose()

        if "env" in locals():
            env.dispose()

if __name__ == "__main__":
    n = 8

    ok, elapsed, solution, status = solve_nqueens_mip(n)

    print("Status:", status)
    print("Có nghiệm:", ok)
    print("Thời gian:", elapsed)

    if solution is None:
                print("No solution found.")
    else:
        for row in solution:
            print(" ".join("Q" if cell else "." for cell in row))
