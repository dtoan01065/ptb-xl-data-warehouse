from pathlib import Path

import numpy as np
import pandas as pd
import wfdb


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "ptb-xl-1.0.3"
METADATA_PATH = DATA_ROOT / "ptbxl_database.csv"

SIGNAL_VARIANTS = (
    ("filename_lr", 100),
    ("filename_hr", 500),
)

SAMPLE_HEADERS_PER_VARIANT = 5


def inspect_sample_headers(rows, column, expected_fs):
    sample_count = min(SAMPLE_HEADERS_PER_VARIANT, len(rows))
    positions = np.linspace(
        0, len(rows) - 1, num=sample_count, dtype=int
    )
    samples = rows.iloc[positions]

    errors = []

    for row in samples.itertuples(index=False):
        ecg_id = row.ecg_id
        record_path = DATA_ROOT / getattr(row, column)

        if not record_path.with_suffix(".hea").is_file():
            continue
        if not record_path.with_suffix(".dat").is_file():
            continue

        try:
            header = wfdb.rdheader(str(record_path))
        except Exception as error:
            errors.append(f"ecg_id={ecg_id}: không đọc được header: {error}")
            continue

        if header.fs != expected_fs:
            errors.append(
                f"ecg_id={ecg_id}: tần số {header.fs}, "
                f"mong đợi {expected_fs}"
            )

        if header.n_sig != 12:
            errors.append(
                f"ecg_id={ecg_id}: có {header.n_sig} đạo trình, mong đợi 12"
            )

        duration = header.sig_len / header.fs
        if abs(duration - 10.0) > 0.02:
            errors.append(
                f"ecg_id={ecg_id}: dài {duration:.3f} giây, "
                "mong đợi khoảng 10 giây"
            )

    return sample_count, errors


def main():
    df = pd.read_csv(METADATA_PATH)
    total_pairs_expected = len(df) * len(SIGNAL_VARIANTS)
    total_pairs_found = 0
    all_errors = []

    print(f"Số ECG trong metadata: {len(df):,}")
    print(f"Số cặp tín hiệu cần kiểm tra: {total_pairs_expected:,}")

    for column, expected_fs in SIGNAL_VARIANTS:
        rows = df[["ecg_id", column]].dropna()
        missing_headers = []
        missing_signals = []
        pairs_found = 0

        for row in rows.itertuples(index=False):
            ecg_id = row.ecg_id
            record_path = DATA_ROOT / getattr(row, column)
            header_path = record_path.with_suffix(".hea")
            signal_path = record_path.with_suffix(".dat")

            if not header_path.is_file():
                missing_headers.append(ecg_id)
            if not signal_path.is_file():
                missing_signals.append(ecg_id)
            if header_path.is_file() and signal_path.is_file():
                pairs_found += 1

        total_pairs_found += pairs_found

        print(f"\n=== {column} ({expected_fs} Hz) ===")
        print(f"Metadata có đường dẫn: {len(rows):,}")
        print(f"Cặp .hea/.dat tìm thấy: {pairs_found:,}")
        print(f"Thiếu .hea: {len(missing_headers):,}")
        print(f"Thiếu .dat: {len(missing_signals):,}")

        if missing_headers:
            all_errors.append(
                f"{column}: thiếu .hea ở ecg_id "
                f"{missing_headers[:10]}"
            )
        if missing_signals:
            all_errors.append(
                f"{column}: thiếu .dat ở ecg_id "
                f"{missing_signals[:10]}"
            )

        sample_count, sample_errors = inspect_sample_headers(
            rows, column, expected_fs
        )
        print(f"Header WFDB đọc thử: {sample_count}")
        all_errors.extend(
            f"{column}: {error}" for error in sample_errors
        )

    print(f"\nTổng cặp .hea/.dat tìm thấy: {total_pairs_found:,}")
    print(f"Tổng cặp dự kiến: {total_pairs_expected:,}")
    print(f"Số vấn đề phát hiện: {len(all_errors):,}")

    if all_errors:
        print("\nMột số vấn đề:")
        for error in all_errors[:20]:
            print(f"- {error}")
    else:
        print(
            "\nKhông phát hiện file bị thiếu; "
            "các header mẫu khớp tần số, số đạo trình và thời lượng."
        )


if __name__ == "__main__":
    main()