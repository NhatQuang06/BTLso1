
import time
import pandas as pd
from pathlib import Path
from binomial import solve_n_queens as solve_binomial
from binary import solve_n_queens as solve_binary
from commander import solve_n_queens as solve_commander
from product import solve_n_queens as solve_product
from sequential import solve_n_queens as solve_sequential

from cpsat_solver import solve_nqueens_cpsat
from mip_solver import solve_nqueens_mip


N_VALUES = [2, 8, 16, 25, 32, 50, 64, 80, 100]
TIMEOUT_SEC = 300

SAT_METHODS = [
    ("SAT-Pairwise", solve_binomial),
    ("SAT-Binary", solve_binary),
    ("SAT-Commander", solve_commander),
    ("SAT-Product", solve_product),
    ("SAT-Sequential", solve_sequential),
]

RESULT_COLUMNS = [
    "N",
    "Method",
    "Status",
    "TotalTime(s)",
    "SolverTime(s)",
    "NumVariables",
    "NumClauses",
    "Error",
]


def validate_board(board):
    """Kiểm tra bàn cờ có phải nghiệm N-Queens hợp lệ không."""
    if board is None:
        return False

    n = len(board)

    if n == 0 or any(len(row) != n for row in board):
        return False

    if any(sum(row) != 1 for row in board):
        return False

    if any(
        sum(board[i][j] for i in range(n)) != 1
        for j in range(n)
    ):
        return False

    positions = [
        (i, j)
        for i in range(n)
        for j in range(n)
        if board[i][j] == 1
    ]

    if len(positions) != n:
        return False

    diag1 = [i - j for i, j in positions]
    diag2 = [i + j for i, j in positions]

    return (
        len(set(diag1)) == n
        and len(set(diag2)) == n
    )


def to_board(solution, n):
    if solution is None:
        return None

    if (
        isinstance(solution, (list, tuple))
        and len(solution) == n
        and all(
            isinstance(row, (list, tuple))
            and len(row) == n
            for row in solution
        )
    ):
        return [list(row) for row in solution]

    if (
        isinstance(solution, (list, tuple))
        and len(solution) == n
        and all(isinstance(col, int) for col in solution)
        and all(0 <= col < n for col in solution)
    ):
        board = [[0] * n for _ in range(n)]
        for i, col in enumerate(solution):
            board[i][col] = 1
        return board

    return None

def normalize_result(result, n):
    """
    Hỗ trợ các định dạng:
    - CP-SAT/MIP:
      (solved, elapsed, solution, status)
    - SAT:
      solution matrix hoặc None
    - Commander:
      (solution, elapsed, num_vars, num_clauses)
    """
    solver_time = None
    num_vars = None
    num_clauses = None
    solution = None

    if isinstance(result, tuple):
        
        if (
            len(result) == 4
            and isinstance(result[0], bool)
            and isinstance(result[3], str)
        ):
            solved, solver_time, solution, status_name = result

            board = to_board(solution, n)

            if board is not None:
                status = "SAT" if validate_board(board) else "INVALID"
            elif status_name == "INFEASIBLE":
                status = "UNSAT"
            else:
                status = "UNKNOWN"

            return status, solver_time, num_vars, num_clauses

        if len(result) == 4:
            solution, solver_time, num_vars, num_clauses = result

            if solution is None:
                status = "UNSAT"
            else:
                status = (
                    "SAT" if validate_board(solution)
                    else "INVALID"
                )

            return status, solver_time, num_vars, num_clauses

        raise ValueError(
            f"Unsupported solver return format: {result!r}"
        )

    if result is None:
        status = "UNSAT"
    else:
        status = (
            "SAT" if validate_board(result)
            else "INVALID"
        )

    return status, solver_time, num_vars, num_clauses


def run_one(method, solver_function, n):
    record = {
        "N": n,
        "Method": method,
        "Status": "ERROR",
        "TotalTime(s)": None,
        "SolverTime(s)": None,
        "NumVariables": None,
        "NumClauses": None,
        "Error": None,
    }

    start = time.perf_counter()

    try:
        result = solver_function(n)
        total_time = time.perf_counter() - start

        status, solver_time, num_vars, num_clauses = (
            normalize_result(result, n)
        )

        record.update({
            "Status": status,
            "TotalTime(s)": total_time,
            "SolverTime(s)": solver_time,
            "NumVariables": num_vars,
            "NumClauses": num_clauses,
        })

    except Exception as exc:
        record["TotalTime(s)"] = time.perf_counter() - start
        record["Error"] = f"{type(exc).__name__}: {exc}"

    return record


def main():
    results = []

    methods = [
        (
            "CP-SAT",
            lambda n: solve_nqueens_cpsat(
                n, timeout_sec=TIMEOUT_SEC
            ),
        ),
        (
            "MIP",
            lambda n: solve_nqueens_mip(
                n, timeout_sec=TIMEOUT_SEC
            ),
        ),
        *SAT_METHODS,
    ]

    for n in N_VALUES:
        print(f"\n========== N = {n} ==========")

        for method, solver_function in methods:
            record = run_one(method, solver_function, n)
            results.append(record)

            total = record["TotalTime(s)"]
            elapsed_text = (
                f"{total:.4f}s"
                if total is not None
                else "N/A"
            )

            print(
                f"{method:18s} | "
                f"{record['Status']:7s} | "
                f"{elapsed_text}"
            )

            if record["Error"]:
                print("  Error:", record["Error"])

    df = pd.DataFrame(results, columns=RESULT_COLUMNS)

    output_file = Path(__file__).resolve().parent / "benchmark_results.csv"

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("\nBenchmark finished.")
    print(f"Saved results to: {output_file}")


if __name__ == "__main__":
    main()
