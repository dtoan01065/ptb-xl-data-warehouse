from pathlib import Path
import subprocess
import sys

from dotenv import dotenv_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

SQL_STEPS = [
    ("sql/01_create_schemas_and_raw_tables.sql", False),
    ("sql/02_build_staging.sql", False),
    ("sql/03_validate_staging.sql", True),
    ("sql/04_build_mart.sql", False),
    ("sql/05_validate_mart.sql", True),
]


def run_sql_file(relative_path: str, validate: bool, settings: dict[str, str | None]) -> None:
    sql_path = PROJECT_ROOT / relative_path

    if not sql_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file SQL: {sql_path}")

    command = [
        "docker", "compose", "exec", "-T", "postgres",
        "psql", "-X", "-v", "ON_ERROR_STOP=1",
        "-U", settings["POSTGRES_USER"],
        "-d", settings["POSTGRES_DB"],
    ]

    if validate:
        command.extend(["-q", "-A", "-t", "-F", "|"])

    result = subprocess.run(
        command,
        input=sql_path.read_text(encoding="utf-8"),
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
    )

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    if result.returncode != 0:
        raise RuntimeError(f"Chạy thất bại: {relative_path}")

    if validate:
        rows = [
            line.strip()
            for line in result.stdout.splitlines()
            if "|" in line
        ]

        if not rows:
            raise RuntimeError(f"Không đọc được kết quả kiểm tra từ {relative_path}")

        failed = [
            row for row in rows
            if row.rsplit("|", 1)[-1].strip().lower() not in {"t", "true"}
        ]

        if failed:
            raise RuntimeError(
                f"Có kiểm tra không đạt trong {relative_path}:\n"
                + "\n".join(failed)
            )

        print(f"Tất cả kiểm tra trong {relative_path} đều đạt.")


def main() -> None:
    if not ENV_FILE.is_file():
        raise FileNotFoundError("Không tìm thấy file .env ở thư mục gốc dự án.")

    settings = dotenv_values(ENV_FILE)
    required = ["POSTGRES_USER", "POSTGRES_DB"]
    missing = [key for key in required if not settings.get(key)]

    if missing:
        raise ValueError(f".env thiếu cấu hình: {', '.join(missing)}")

    print("=== 1/6: Tạo hoặc xác nhận raw schema và bảng ===")
    run_sql_file(SQL_STEPS[0][0], False, settings)

    print("=== 2/6: Nạp lại dữ liệu raw ===")
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "load_raw.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )

    for step_number, (sql_file, validate) in enumerate(SQL_STEPS[1:], start=3):
        print(f"=== {step_number}/6: {sql_file} ===")
        run_sql_file(sql_file, validate, settings)

    print("Pipeline hoàn tất: raw → staging → mart.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"PIPELINE FAILED: {error}", file=sys.stderr)
        sys.exit(1)