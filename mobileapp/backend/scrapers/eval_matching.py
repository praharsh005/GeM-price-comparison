import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.matching import _score, normalize_name

EVAL_PAIRS = Path(__file__).resolve().parent.parent / "eval_pairs.csv"


def main() -> None:
    rows = list(csv.DictReader(EVAL_PAIRS.open(encoding="utf-8")))
    scored = []
    for r in rows:
        sim, cov = _score(normalize_name(r["a_name"]), normalize_name(r["b_name"]))
        scored.append((sim, cov, r["gold"]))

    print(f"labeled pairs: {len(scored)}")
    for threshold, min_cov, label in [
        (85.0, 0.55, "high (85/0.55)"),
        (75.0, 0.35, "medium (75/0.35)"),
        (65.0, 0.30, "low (65/0.30)"),
    ]:
        tp = sum(1 for s, c, g in scored if s >= threshold and c >= min_cov and g == "yes")
        fp = sum(1 for s, c, g in scored if s >= threshold and c >= min_cov and g == "no")
        fn = sum(1 for s, c, g in scored if g == "yes" and not (s >= threshold and c >= min_cov))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        print(
            f"threshold {label}: tp={tp} fp={fp} fn={fn} "
            f"precision={precision:.2f} recall={recall:.2f} f1={f1:.2f}"
        )

    print("\nscores per pair (threshold line at sim=85 / cov=0.55):")
    for s, c, g in sorted(scored, reverse=True):
        flag = "P" if s >= 85.0 and c >= 0.55 else "-"
        print(f"  {flag} sim={s:6.1f} cov={c:.2f} gold={g}")


if __name__ == "__main__":
    main()
