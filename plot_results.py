
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "benchmark_results.csv"
OUTPUT_FILE = BASE_DIR / "benchmark_chart.png"

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Không tìm thấy file dữ liệu: {INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

time_column = "TotalTime(s)"

required_columns = {
    "N", "Method", "Status", time_column
}
missing = required_columns - set(df.columns)

if missing:
    raise ValueError(
        f"Thiếu các cột trong CSV: {sorted(missing)}"
    )

df["N"] = pd.to_numeric(df["N"], errors="coerce")
df[time_column] = pd.to_numeric(
    df[time_column], errors="coerce"
)

plot_df = df[
    df["Status"].astype(str).str.strip().str.upper() == "SAT"
].copy()

plot_df = plot_df.dropna(
    subset=["N", "Method", time_column]
)
plot_df = plot_df[plot_df[time_column] > 0]

if plot_df.empty:
    raise ValueError(
        "Không có lượt SAT nào có thời gian hợp lệ."
    )

fig, ax = plt.subplots(figsize=(12, 7))

for method, sub in plot_df.groupby("Method"):
    sub = sub.sort_values("N")

    ax.plot(
        sub["N"],
        sub[time_column],
        marker="o",
        linewidth=2,
        markersize=5,
        label=method
    )

ax.set_xlabel("Kích thước bàn cờ (N)")
ax.set_ylabel("Tổng thời gian chạy (giây)")
ax.set_title(
    "So sánh hiệu năng các thuật toán N-Queens"
)
ax.set_yscale("log")

ax.grid(
    True,
    which="both",
    linestyle="--",
    alpha=0.5
)

ax.legend()
fig.tight_layout()

fig.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(f"Đã lưu biểu đồ tại: {OUTPUT_FILE}")
print(
    f"Số lượt SAT được vẽ: {len(plot_df)}"
)
