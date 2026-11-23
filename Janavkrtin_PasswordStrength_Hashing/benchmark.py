"""
Experiment: how password length, character set, and hash choice affect
how long an exhaustive search would take.


"""
import csv
import hashlib
import math
import os
import time
from pathlib import Path

import bcrypt
from argon2 import PasswordHasher

OUT = Path(__file__).with_name("results")
OUT.mkdir(exist_ok=True)

CHARSETS = {
    "digits (10)": 10,
    "lowercase (26)": 26,
    "upper+lower (52)": 52,
    "alphanumeric (62)": 62,
    "all printable (95)": 95,
}
LENGTHS = [6, 8, 10, 12, 14]
SAMPLE_PW = b"benchmark-pass"


def time_per_hash(fn, runs: int) -> float:
    fn()  # warm-up
    start = time.perf_counter()
    for _ in range(runs):
        fn()
    return (time.perf_counter() - start) / runs


def measure() -> dict:
    ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
    salt = bcrypt.gensalt(12)
    return {
        "SHA-256 (unsalted)": time_per_hash(lambda: hashlib.sha256(SAMPLE_PW).digest(), 200_000),
        "bcrypt (cost 12)": time_per_hash(lambda: bcrypt.hashpw(SAMPLE_PW, salt), 5),
        "Argon2id (19 MiB, t=2)": time_per_hash(lambda: ph.hash(SAMPLE_PW), 10),
    }


def human(seconds: float) -> str:
    if seconds < 1:
        return "< 1 second"
    units = [("years", 31_557_600), ("days", 86_400), ("hours", 3_600), ("minutes", 60), ("seconds", 1)]
    for name, size in units:
        if seconds >= size:
            v = seconds / size
            if name == "years" and v >= 1e6:
                return f"{v:.1e} years"
            return f"{v:,.1f} {name}"
    return f"{seconds:.1f} seconds"


def main() -> None:
    print(f"CPU: {os.cpu_count()} logical cores (single core used)\n")
    timings = measure()

    lines = ["| Hash | Time per hash | Hashes / second (1 core) |", "|---|---|---|"]
    for name, t in timings.items():
        lines.append(f"| {name} | {t * 1000:.4f} ms | {1 / t:,.0f} |")
    (OUT / "hash_timing.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), "\n")

    rows = []
    for cs_name, cs in CHARSETS.items():
        for L in LENGTHS:
            keyspace = cs ** L
            row = {"charset": cs_name, "length": L, "keyspace": f"{keyspace:.2e}",
                   "entropy_bits": round(L * math.log2(cs), 1)}
            for h, t in timings.items():
                row[h] = keyspace * t
            rows.append(row)

    hash_names = list(timings)
    with (OUT / "crack_time_table.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["charset", "length", "entropy_bits", "keyspace"] + [f"{h} worst-case seconds" for h in hash_names])
        for r in rows:
            w.writerow([r["charset"], r["length"], r["entropy_bits"], r["keyspace"]] + [f"{r[h]:.3e}" for h in hash_names])

    md = ["| Character set | Length | Entropy (bits) | " + " | ".join(hash_names) + " |",
          "|---|---|---|" + "---|" * len(hash_names)]
    for r in rows:
        md.append(f"| {r['charset']} | {r['length']} | {r['entropy_bits']} | "
                  + " | ".join(human(r[h]) for h in hash_names) + " |")
    (OUT / "crack_time_table.md").write_text(
        "Worst-case exhaustive search time on ONE CPU core (estimated = keyspace x measured time per hash).\n\n"
        + "\n".join(md) + "\n")
    print("\n".join(md))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
        colors = ["#c0392b", "#2471a3", "#1e8449"]
        for ax, cs_name in zip(axes, ["lowercase (26)", "all printable (95)"]):
            sub = [r for r in rows if r["charset"] == cs_name]
            for h, c in zip(hash_names, colors):
                ax.plot([r["length"] for r in sub], [r[h] / 31_557_600 for r in sub],
                        marker="o", color=c, label=h)
            ax.set_yscale("log")
            ax.set_title(f"Character set: {cs_name}")
            ax.set_xlabel("Password length")
            ax.axhline(1, color="grey", ls="--", lw=0.8)
            ax.text(LENGTHS[-1] - 1.2, 0.15, "1 year", color="grey", fontsize=8)
            ax.grid(True, which="major", alpha=0.3)
        axes[0].set_ylabel("Worst-case search time (years, log scale)")
        axes[0].legend()
        fig.suptitle("Estimated exhaustive-search time, single CPU core")
        fig.tight_layout()
        fig.savefig(OUT / "crack_time_chart.png", dpi=150)
        print(f"\nChart saved to {OUT / 'crack_time_chart.png'}")
    except ImportError:
        print("matplotlib not installed - skipping chart")


if __name__ == "__main__":
    main()
