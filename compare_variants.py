import csv
from pathlib import Path

PAIRS_FILE = "pairs.csv"
FILES_DIR  = "tsv_files"
HAS_HEADER = False

def load_variants(filepath, has_header=False):
    variants = {}
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        if has_header:
            next(reader)
        for row in reader:
            if len(row) < 3:
                continue
            key = (row[0].strip(), row[1].strip(), row[2].strip())
            variants[key] = row
    return variants

def compare_pair(file1, file2, has_header=False):
    data1 = load_variants(file1, has_header)
    data2 = load_variants(file2, has_header)

    keys1  = set(data1.keys())
    keys2  = set(data2.keys())
    shared = keys1 & keys2
    total  = len(keys1 | keys2)

    origin = f"{file1.stem}, {file2.stem}"
    rows = []
    for k in sorted(shared, key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        r1 = data1[k][3:]
        r2 = data2[k][3:]
        r1 += [''] * (3 - len(r1))
        r2 += [''] * (3 - len(r2))
        rows.append([origin] + list(k) + r1[:3] + r2[:3])

    return rows, {
        "SampleA":     file1.name,
        "SampleB":     file2.name,
        "F1_Variants": len(keys1),
        "F2_Variants": len(keys2),
        "Shared":      len(shared),
        "Only_F1":     len(keys1 - keys2),
        "Only_F2":     len(keys2 - keys1),
        "Overlap_%":   f"{len(shared)/total*100:.1f}" if total > 0 else "0.0",
    }

def run_batch(pairs_file, files_dir, has_header=False):
    files_dir = Path(files_dir)

    with open(pairs_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip "SampleA, SampleB" header
        pairs = [(row[0].strip(), row[1].strip())
                 for row in reader if len(row) >= 2]

    total_pairs = len(pairs)
    print(f"Starting batch: {total_pairs} pairs to compare...")

    all_rows     = []
    summary_rows = []
    skipped      = 0

    for i, (f1_name, f2_name) in enumerate(pairs, 1):
        f1 = files_dir / f1_name
        f2 = files_dir / f2_name

        if not f1.exists() or not f2.exists():
            skipped += 1
            continue

        rows, result = compare_pair(f1, f2, has_header)
        all_rows.extend(rows)
        summary_rows.append(result)

        pct = i / total_pairs * 100
        print(f"  Progress: {i}/{total_pairs} ({pct:.1f}%)", end='\r', flush=True)

    if not summary_rows:
        print("No pairs were processed — check your file paths!")
        return

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    # single combined results file
    results_file = out_dir / "comparison_results.csv"
    with open(results_file, "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["Origin", "Position", "Ref", "Alt",
                    "F1_Frequency", "F1_Depth", "F1_DP4",
                    "F2_Frequency", "F2_Depth", "F2_DP4"])
        w.writerows(all_rows)

    # summary of every pair
    summary_file = out_dir / "summary.csv"
    with open(summary_file, "w", newline='') as f:
        w = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        w.writeheader()
        w.writerows(summary_rows)

    print(f"\nDone! {len(summary_rows)}/{total_pairs} pairs processed.", end='')
    if skipped:
        print(f" ({skipped} skipped — missing files)", end='')
    print(f"\nAll shared variants : {results_file.resolve()}")
    print(f"Summary table       : {summary_file.resolve()}")

run_batch(PAIRS_FILE, FILES_DIR, has_header=HAS_HEADER)