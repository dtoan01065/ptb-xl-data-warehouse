from ast import literal_eval
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "ptb-xl-1.0.3"

METADATA_PATH = DATA_ROOT / "ptbxl_database.csv"
STATEMENTS_PATH = DATA_ROOT / "scp_statements.csv"


def parse_scp_codes(value):
    if pd.isna(value):
        return {}

    try:
        parsed = literal_eval(value)
    except (ValueError, SyntaxError):
        return {}

    return parsed if isinstance(parsed, dict) else {}


def main():
    ecg = pd.read_csv(METADATA_PATH)
    statements = pd.read_csv(STATEMENTS_PATH, index_col=0)

    print("=== Thuộc tính bệnh nhân ===")
    distinct_sex_by_patient = ecg.groupby("patient_id")["sex"].nunique(
        dropna=True
    )
    patients_with_multiple_sex_values = (distinct_sex_by_patient > 1).sum()

    print(f"Bệnh nhân có nhiều giá trị sex: {patients_with_multiple_sex_values:,}")
    print(f"Dòng ECG thiếu sex: {ecg['sex'].isna().sum():,}")
    print("Giá trị sex trong nguồn:")
    print(ecg["sex"].value_counts(dropna=False).sort_index().to_string())

    print("\n=== Từ điển mã SCP ===")
    print(f"Số mã trong scp_statements.csv: {len(statements):,}")
    print(f"Các cột mô tả mã: {statements.columns.tolist()}")
    print(f"Mã bị lặp trong từ điển: {statements.index.duplicated().sum():,}")

    observed_codes = set()
    parse_failures = 0

    for value in ecg["scp_codes"].dropna():
        codes = parse_scp_codes(value)
        if not codes:
            parse_failures += 1
        observed_codes.update(codes.keys())

    known_codes = set(statements.index.astype(str))
    unknown_codes = sorted(observed_codes - known_codes)

    print(f"Số mã SCP khác nhau trong metadata: {len(observed_codes):,}")
    print(f"Dòng scp_codes không phân tích được: {parse_failures:,}")
    print(f"Mã metadata không có trong từ điển: {len(unknown_codes):,}")

    if unknown_codes:
        print("Các mã chưa tra được:", unknown_codes)


if __name__ == "__main__":
    main()