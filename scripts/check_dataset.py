from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "ptb-xl-1.0.3"
CSV_PATH = DATA_ROOT / "ptbxl_database.csv"


def main():
    df = pd.read_csv(CSV_PATH)

    print(f"Số bản ghi metadata: {len(df):,}")
    print(f"Số cột metadata: {len(df.columns)}")

    for column in ("filename_lr", "filename_hr"):
        filenames = df[column].dropna()
        existing = sum(
            (DATA_ROOT / filename).with_suffix(".hea").is_file()
            for filename in filenames
        )
        print(f"{column}: {existing:,}/{len(filenames):,} file .hea tồn tại")

    print("\nTỷ lệ thiếu theo cột, cao nhất trước:")
    missing_percent = (df.isna().mean() * 100).sort_values(ascending=False)
    print(missing_percent.head(15).round(1).to_string())


if __name__ == "__main__":
    main()