import csv
from pathlib import Path

FILES_DIR  = "tsv_files"
OUTPUT_FILE = "results/combined.tsv"
HAS_HEADER = False

def combine_tsvs(files_dir, output_file, has_header=False):
    files_dir = Path(files_dir)
    tsv_files = sorted(files_dir.glob("*.tsv"))

    if not tsv_files:
        print(f"No TSV files found in {files_dir.resolve()}")
        return

    print(f"Combining {len(tsv_files)} TSV files...")

    all_rows = []
    for tsv_path in tsv_files:
        source = tsv_path.stem
        with open(tsv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            if has_header:
                next(reader)
            for row in reader:
                if not row or all(cell.strip() == '' for cell in row):
                    continue
                all_rows.append([source] + row)

    out_path = Path(output_file)
    out_path.parent.mkdir(exist_ok=True)

    with open(out_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["Source", "Position", "Ref", "Alt", "Frequency", "Depth", "DP4"])
        writer.writerows(all_rows)

    print(f"Done! {len(all_rows)} rows written to {out_path.resolve()} :-)")

combine_tsvs(FILES_DIR, OUTPUT_FILE, has_header=HAS_HEADER)
