# PTB-XL Data Warehouse

Dự án xây dựng pipeline dữ liệu và data warehouse cho metadata ECG trong bộ PTB-XL. Mục tiêu là đưa dữ liệu từ các file nguồn vào PostgreSQL, kiểm tra chất lượng, chuẩn hóa thành các tầng dữ liệu và tạo mô hình mart phục vụ truy vấn phân tích.

> Đây là dự án Data Engineering phục vụ học tập và trình diễn kỹ thuật. Dự án không phải công cụ chẩn đoán, không đưa ra khuyến nghị y tế và không đánh giá hiệu quả lâm sàng.

## Bài toán

PTB-XL gồm metadata ECG, từ điển mã SCP và tín hiệu ECG lưu thành nhiều file WFDB. Nếu đọc trực tiếp các file nguồn cho từng báo cáo thì khó quản lý lineage, kiểm tra tính nhất quán và tái sử dụng dữ liệu.

Một số đặc điểm cần xử lý trong quá trình xây dựng warehouse:

- Một bệnh nhân có thể có nhiều bản ghi ECG.
- Một ECG có thể mang nhiều mã SCP, nên quan hệ ECG–mã chẩn đoán là quan hệ nhiều-nhiều.
- Metadata có các trường thiếu; giá trị thiếu không mặc nhiên có nghĩa là `false`.
- Bộ dữ liệu mã hóa tuổi trên 89 theo giá trị `300`. Giá trị này không phải tuổi thực để tính toán. [Tài liệu PTB-XL trên PhysioNet](https://physionet.org/content/ptb-xl/1.0.3/)
- Ngày ghi ECG được dịch chuyển ngẫu nhiên theo từng bệnh nhân, do đó không phù hợp để kết luận xu hướng thời gian giữa các bệnh nhân. [Tài liệu PTB-XL trên PhysioNet](https://physionet.org/content/ptb-xl/1.0.3/)

## Cách giải quyết

Dự án tổ chức dữ liệu thành ba tầng:

1. **Raw** lưu dữ liệu nguồn được nạp vào PostgreSQL, gồm metadata ECG và từ điển mã SCP.
2. **Staging** chuẩn hóa metadata ECG, xử lý tuổi đặc biệt và tách `scp_codes` thành các dòng quan hệ ECG–SCP.
3. **Mart** tổ chức dữ liệu theo mô hình dimensional/star schema để truy vấn phân tích.

Pipeline được chạy bằng một lệnh Python. Script gọi các file SQL theo thứ tự, chạy kiểm tra chất lượng và dừng khi có lỗi hoặc một kiểm tra không đạt.

## Kiến trúc

```text
PTB-XL CSV files
       │
       ▼
Python raw loader ───────────────► PostgreSQL: raw
                                      │
                                      ▼
                              PostgreSQL: staging
                                      │
                                      ▼
                                PostgreSQL: mart
                                      │
                                      ▼
                         SQL analytics queries
```

PostgreSQL chạy trong Docker Compose. Python nạp dữ liệu nguồn; SQL thực hiện biến đổi, xây dựng bảng và kiểm tra dữ liệu.

## Mô hình dữ liệu

### Raw

- `raw.ptbxl_ecg_source`: metadata nguồn, một dòng cho mỗi ECG.
- `raw.ptbxl_scp_statement_source`: từ điển mã SCP.

### Staging

- `staging.stg_ecg`: một dòng cho mỗi ECG; giữ tuổi nguồn, tạo tuổi phân tích và cờ `age_90_plus`.
- `staging.bridge_ecg_scp`: một dòng cho mỗi cặp ECG–mã SCP, gồm điểm `likelihood` từ nguồn.

### Mart

| Bảng | Grain — ý nghĩa của một dòng |
|---|---|
| `mart.dim_patient` | Một dòng cho mỗi bệnh nhân |
| `mart.dim_scp_statement` | Một dòng cho mỗi mã SCP |
| `mart.fact_ecg_recording` | Một dòng cho mỗi ECG |
| `mart.fact_ecg_scp` | Một dòng cho mỗi cặp ECG–mã SCP |

Tuổi nằm trong fact ECG vì đó là tuổi tại lần ghi ECG, không phải thuộc tính cố định của bệnh nhân. `likelihood` được giữ như điểm do bộ dữ liệu cung cấp; dự án không diễn giải điểm đó thành xác suất bệnh đã hiệu chuẩn.

## Bộ dữ liệu và nguồn

Dự án dùng **PTB-XL phiên bản 1.0.3** từ PhysioNet. Theo mô tả bộ dữ liệu, phiên bản này có **21.799 ECG 12 đạo trình từ 18.869 bệnh nhân**, với các ECG dài 10 giây và từ điển 71 statement SCP. [PhysioNet: PTB-XL v1.0.3](https://physionet.org/content/ptb-xl/1.0.3/)

Bộ dữ liệu cung cấp tín hiệu WFDB ở 100 Hz và 500 Hz, metadata trong `ptbxl_database.csv`, cùng từ điển mã trong `scp_statements.csv`. [PhysioNet: mô tả và cấu trúc dữ liệu](https://physionet.org/content/ptb-xl/1.0.3/)

- Trang bộ dữ liệu: [PTB-XL v1.0.3 trên PhysioNet](https://physionet.org/content/ptb-xl/1.0.3/)
- DOI: [10.13026/kfzx-aw45](https://doi.org/10.13026/kfzx-aw45)
- Giấy phép bộ dữ liệu: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- Bài báo mô tả bộ dữ liệu: [Wagner et al., Scientific Data, 2020](https://doi.org/10.1038/s41597-020-0495-6)

Dữ liệu gốc không được lưu trong repository. Người dùng cần tải dữ liệu từ PhysioNet và đặt trong thư mục `data/ptb-xl-1.0.3/`. Hãy tuân theo giấy phép và trích dẫn nguồn khi sử dụng hoặc phân phối dữ liệu.

## Kết quả đã kiểm tra

Các kết quả dưới đây là từ lần chạy và kiểm tra trên môi trường phát triển cục bộ:

- **21.799** ECG metadata, không trùng `ecg_id`.
- **18.869** bệnh nhân.
- **71** mã SCP trong từ điển.
- **61.007** cặp ECG–SCP sau khi tách mã nhiều nhãn.
- **293** bản ghi có tuổi nguồn `300`; staging đánh dấu nhóm `90+` và không dùng `300` như tuổi thật.
- Đã đối chiếu **87.203 file** trong manifest SHA-256; không phát hiện file thiếu hoặc checksum sai.
- Đã kiểm tra inventory các file WFDB 100 Hz/500 Hz: các cặp `.hea`/`.dat` đều hiện diện; header mẫu khớp tần số lấy mẫu, 12 đạo trình và thời lượng 10 giây.
- Kiểm tra chất lượng staging và mart đạt: số dòng khớp, ID và cặp ECG–SCP không trùng, không phát hiện mã SCP ngoài từ điển.

Các kết quả trên là kết quả của bộ dữ liệu cục bộ được kiểm tra; chúng không thay thế việc chạy lại kiểm tra trên một bản tải mới.

## Công nghệ

- Python
- PostgreSQL 16
- Docker Compose
- Psycopg 3
- SQL
- WFDB, pandas và PyArrow cho một số bước kiểm tra dữ liệu

## Cấu trúc repository

```text
.
├── data/                         # Dữ liệu cục bộ; không đưa lên Git
├── docs/
│   └── data_model.md             # Ghi chú mô hình dữ liệu
├── scripts/
│   ├── check_dataset.py          # Kiểm tra metadata và đường dẫn tín hiệu
│   ├── profile_dataset.py        # Thống kê metadata
│   ├── check_wfdb.py             # Đọc thử tín hiệu WFDB
│   ├── validate_wfdb_inventory.py
│   ├── verify_checksums.py       # Đối chiếu SHA-256
│   ├── check_model_assumptions.py
│   ├── load_raw.py               # Nạp CSV nguồn vào raw
│   └── run_pipeline.py           # Chạy pipeline raw → staging → mart
├── sql/
│   ├── 01_create_schemas_and_raw_tables.sql
│   ├── 02_build_staging.sql
│   ├── 03_validate_staging.sql
│   ├── 04_build_mart.sql
│   ├── 05_validate_mart.sql
│   └── 06_analytics_queries.sql
├── .env.example
├── .gitignore
├── compose.yaml
└── README.md
```

## Cài đặt và chạy trên Windows

Các lệnh dưới đây chạy trong PowerShell tại thư mục gốc dự án.

### 1. Chuẩn bị bộ PTB-XL

Tải phiên bản 1.0.3 từ [PhysioNet](https://physionet.org/content/ptb-xl/1.0.3/) và giải nén thành cấu trúc:

```text
data/
└── ptb-xl-1.0.3/
    ├── ptbxl_database.csv
    ├── scp_statements.csv
    ├── SHA256SUMS.txt
    ├── records100/
    └── records500/
```

### 2. Tạo môi trường Python

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "psycopg[binary]" python-dotenv pandas wfdb pyarrow
```

### 3. Cấu hình PostgreSQL

Tạo file `.env` từ mẫu:

```powershell
Copy-Item .env.example .env
```

Mở `.env` và điền cấu hình PostgreSQL. Không commit hoặc chia sẻ file `.env`; file này chứa thông tin kết nối bí mật.

### 4. Khởi động PostgreSQL

Đảm bảo Docker Desktop đang chạy, sau đó:

```powershell
docker compose up -d postgres
docker compose ps
```

Chờ đến khi container PostgreSQL ở trạng thái healthy.

### 5. Chạy toàn bộ pipeline

Tại thư mục gốc dự án:

```powershell
python .\scripts\run_pipeline.py
```

Pipeline chạy theo thứ tự:

1. Tạo hoặc xác nhận schema và bảng raw.
2. Nạp lại metadata ECG và từ điển SCP.
3. Xây dựng staging.
4. Kiểm tra chất lượng staging.
5. Xây dựng mart.
6. Kiểm tra chất lượng mart.

Pipeline chỉ báo hoàn tất nếu các bước chạy thành công và các truy vấn kiểm tra đạt.

### 6. Chạy truy vấn phân tích

Mở `sql/06_analytics_queries.sql` trong VS Code, kết nối tới database `ptbxl_warehouse` trên `localhost:5432`, rồi chạy từng truy vấn. Các truy vấn mẫu phân tích mã SCP, nhóm chẩn đoán, tuổi/giới tính, mức độ thiếu dữ liệu và fold.

## Hành vi khi chạy lại

Pipeline hiện chạy theo kiểu **full refresh**. Mỗi lần chạy sẽ nạp lại dữ liệu raw và xây dựng lại staging/mart từ đầu. Pipeline chưa hỗ trợ incremental load, lập lịch hoặc khôi phục từng bước theo checkpoint.

Với bộ dữ liệu PTB-XL v1.0.3 đã kiểm tra, số dòng kỳ vọng ở mart là:

| Bảng | Số dòng |
|---|---:|
| `mart.dim_patient` | 18.869 |
| `mart.dim_scp_statement` | 71 |
| `mart.fact_ecg_recording` | 21.799 |
| `mart.fact_ecg_scp` | 61.007 |

## Lưu ý khi phân tích

- Một ECG có thể mang nhiều mã SCP. Vì vậy, các thống kê theo mã hoặc nhóm chẩn đoán có thể chồng lấp và tổng số của chúng có thể lớn hơn số ECG.
- Tuổi `300` trong nguồn được xử lý thành cờ nhóm `90+`; không diễn giải thành tuổi 300.
- Ngày ghi đã được dịch chuyển ngẫu nhiên theo từng bệnh nhân, không dùng để kết luận xu hướng lịch sử giữa bệnh nhân.
- Dữ liệu thiếu không mặc nhiên có nghĩa là giá trị bằng 0 hoặc `false`.
- Điểm `likelihood` được giữ theo nguồn, không được xem là xác suất dự đoán đã hiệu chuẩn.
- Các phân tích chỉ mô tả nội dung bộ dữ liệu; không suy ra quan hệ nhân quả hoặc kết luận lâm sàng.

## Hướng phát triển

- Thêm kiểm thử tự động và kiểm tra schema trong CI.
- Thiết kế incremental load và chiến lược xử lý dữ liệu đến muộn.
- Thêm orchestration/scheduling khi pipeline cơ bản ổn định.
- Tạo dashboard đọc dữ liệu từ mart.
- Mở rộng xử lý tín hiệu ECG nếu có yêu cầu phân tích waveform.

## Trích dẫn

Khi sử dụng PTB-XL, hãy trích dẫn bộ dữ liệu và bài báo gốc theo hướng dẫn của [PhysioNet](https://physionet.org/content/ptb-xl/1.0.3/):

> Wagner, P., Strodthoff, N., Bousseljot, R.-D., Kreiseler, D., Lunze, F. I., Samek, W., & Schaeffter, T. (2020). PTB-XL: A Large Publicly Available ECG Dataset. *Scientific Data*. https://doi.org/10.1038/s41597-020-0495-6
