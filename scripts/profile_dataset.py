from ast import literal_eval
from collections import Counter
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "ptb-xl-1.0.3"
METADATA_PATH = DATA_ROOT / "ptbxl_database.csv"


def parse_scp_codes(value):
    """Chuyển chuỗi dict SCP trong CSV thành dict Python."""
    if pd.isna(value):
        return {}

    try:
        parsed = literal_eval(value)
    except (ValueError, SyntaxError):
        return {}

    return parsed if isinstance(parsed, dict) else {}


def main():
    df = pd.read_csv(METADATA_PATH)

    print("=== Khóa và quan hệ ===")
    print(f"ECG ID duy nhất: {df['ecg_id'].nunique():,}")
    print(f"ECG ID bị trùng: {df['ecg_id'].duplicated().sum():,}")
    print(f"Bệnh nhân duy nhất: {df['patient_id'].nunique():,}")
    print(f"Bản ghi thiếu patient_id: {df['patient_id'].isna().sum():,}")

    ecgs_per_patient = df.groupby("patient_id")["ecg_id"].count()
    print("\nSố ECG trên mỗi bệnh nhân:")
    print(ecgs_per_patient.describe().round(2).to_string())

    print("\n=== Tuổi ===")
    print(df["age"].describe().round(2).to_string())
    print(f"Tuổi >= 300: {(df['age'] >= 300).sum():,}")

    print("\n=== Ngày ghi ===")
    dates = pd.to_datetime(df["recording_date"], errors="coerce")
    print(f"Ngày không đọc được: {dates.isna().sum():,}")
    print(f"Ngày sớm nhất: {dates.min()}")
    print(f"Ngày muộn nhất: {dates.max()}")

    print("\n=== Mã SCP phổ biến nhất ===")
    code_counts = Counter()
    parse_failures = 0

    for value in df["scp_codes"].dropna():
        codes = parse_scp_codes(value)
        if not codes:
            parse_failures += 1
        code_counts.update(codes.keys())

    print(f"Dòng scp_codes không phân tích được: {parse_failures:,}")
    for code, count in code_counts.most_common(15):
        print(f"{code}: {count:,}")


if __name__ == "__main__":
    main()