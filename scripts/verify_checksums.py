import hashlib
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "ptb-xl-1.0.3"
MANIFEST_PATH = DATA_ROOT / "SHA256SUMS.txt"
CHUNK_SIZE = 1024 * 1024


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(CHUNK_SIZE):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    checked = 0
    missing = []
    mismatched = []
    malformed = []

    with MANIFEST_PATH.open("r", encoding="utf-8-sig") as manifest:
        entries = [line.strip() for line in manifest if line.strip()]

    total = len(entries)
    print(f"Số dòng trong manifest: {total:,}")

    for line_number, entry in enumerate(entries, start=1):
        parts = entry.split(maxsplit=1)

        if len(parts) != 2:
            malformed.append(f"Dòng {line_number}: sai định dạng")
            continue

        expected_hash, relative_name = parts

        if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
            malformed.append(f"Dòng {line_number}: mã SHA-256 không hợp lệ")
            continue

        file_path = DATA_ROOT / relative_name

        if not file_path.is_file():
            missing.append(relative_name)
            continue

        actual_hash = calculate_sha256(file_path)
        checked += 1

        if actual_hash.lower() != expected_hash.lower():
            mismatched.append(relative_name)

        if checked and checked % 500 == 0:
            print(f"Đã kiểm tra {checked:,} file...")

    print("\n=== Kết quả ===")
    print(f"File đã băm và đối chiếu: {checked:,}")
    print(f"File thiếu: {len(missing):,}")
    print(f"Checksum không khớp: {len(mismatched):,}")
    print(f"Dòng manifest lỗi: {len(malformed):,}")

    for label, items in (
        ("File thiếu", missing),
        ("Checksum không khớp", mismatched),
        ("Dòng lỗi", malformed),
    ):
        if items:
            print(f"\n{label} — tối đa 20 mục đầu:")
            for item in items[:20]:
                print(f"- {item}")

    if missing or mismatched or malformed:
        raise SystemExit(1)

    print("\nTất cả file trong manifest đều khớp checksum.")


if __name__ == "__main__":
    main()