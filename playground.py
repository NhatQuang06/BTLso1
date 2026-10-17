import time
import product

board_sizes = [4, 8, 16, 32, 64, 128, 256, 512]

def main():
    for n in board_sizes:
        print(f"\n===== N = {n} =====")

        start = time.perf_counter()

        try:
            solution = product.solve_n_queens(n)
            elapsed = time.perf_counter() - start

            if solution is None:
                print("Không tìm thấy nghiệm.")
            else:
                print("Tìm thấy nghiệm.")

            print(f"Thời gian tổng: {elapsed:.4f} giây")

        except Exception as exc:
            elapsed = time.perf_counter() - start
            print(f"Lỗi: {type(exc).__name__}: {exc}")
            print(f"Thời gian trước lỗi: {elapsed:.4f} giây")


if __name__ == "__main__":
    main()