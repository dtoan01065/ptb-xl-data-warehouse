from pathlib import Path

import numpy as np
import pandas as pd
import wfdb


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "ptb-xl-1.0.3"
METADATA_PATH = DATA_ROOT / "ptbxl_database.csv"


def inspect_record(ecg_id: int, column: str, expected_fs: int) -> None:
    df = pd.read_csv(METADATA_PATH)
    row = df.loc[df["ecg_id"] == ecg_id]

    if row.empty:
        raise ValueError(f"Không tìm thấy ecg_id={ecg_id}")

    relative_path = row.iloc[0][column]
    record_path = DATA_ROOT / relative_path

    header_path = record_path.with_suffix(".hea")
    signal_path = record_path.with_suffix(".dat")

    print(f"\n=== {column}: {relative_path} ===")
    print(f"Header tồn tại: {header_path.is_file()}")
    print(f"Signal tồn tại: {signal_path.is_file()}")

    if not header_path.is_file() or not signal_path.is_file():
        raise FileNotFoundError(f"Thiếu file WFDB cho ecg_id={ecg_id}")

    record = wfdb.rdrecord(str(record_path))
    signal = record.p_signal

    print(f"Tần số lấy mẫu: {record.fs} Hz (mong đợi {expected_fs} Hz)")
    print(f"Số đạo trình: {record.n_sig}")
    print(f"Tên đạo trình: {record.sig_name}")
    print(f"Đơn vị: {record.units}")
    print(f"Kích thước tín hiệu: {signal.shape} (mẫu, đạo trình)")
    print(f"Thời lượng: {record.sig_len / record.fs:.2f} giây")
    print(f"Tất cả giá trị là số hữu hạn: {np.isfinite(signal).all()}")

    if record.fs != expected_fs:
        raise ValueError(
            f"Tần số không khớp: đọc được {record.fs}, mong đợi {expected_fs}"
        )

    if record.n_sig != 12:
        raise ValueError(f"Mong đợi 12 đạo trình, đọc được {record.n_sig}")


def main() -> None:
    inspect_record(ecg_id=1, column="filename_lr", expected_fs=100)
    inspect_record(ecg_id=1, column="filename_hr", expected_fs=500)


if __name__ == "__main__":
    main()