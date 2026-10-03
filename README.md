Tóm tắt dự án: PTB-XL Data Warehouse
1. Mục tiêu
Xây dựng một dự án Data Engineering end to end để luyện các kỹ năng thường dùng khi xây dựng kho dữ liệu:
- Đọc dữ liệu thô từ nhiều file.
- Kiểm tra tính toàn vẹn và chất lượng dữ liệu.
- Thiết kế schema quan hệ và mô hình dữ liệu dạng star schema.
- Nạp dữ liệu có thể chạy lại mà không tạo bản ghi trùng.
- Biến đổi dữ liệu bằng SQL/dbt.
- Tạo các bảng tổng hợp phục vụ phân tích.
Đây là dự án kỹ thuật dữ liệu nghiên cứu, không phải công cụ chẩn đoán hay tư vấn y tế.
2. Bộ dữ liệu hiện có
Sếp đã tải và giải nén PTB-XL phiên bản 1.0.3 tại:
D:\DE_Starter\data\ptb-xl-1.0.3
Thư mục hiện có:
- ptbxl_database.csv: metadata ECG, 21.799 hàng và 28 cột theo lần đọc vừa thực hiện.
- scp_statements.csv: mô tả các mã SCP.
- records100 và records500: tín hiệu ECG ở hai tần số lấy mẫu.
- RECORDS, LICENSE.txt, các file changelog và SHA256SUMS.txt.
Metadata có thông tin như ecg_id, patient_id, tuổi, giới tính, ngày ghi, mã SCP và đường dẫn đến file tín hiệu. Nhiều trường có thể bị thiếu; cần đo và ghi nhận trước khi xử lý, không tự điền tùy tiện.
3. Phạm vi hợp lý cho bản đầu tiên
Tập trung vào Data Warehouse và pipeline, chưa làm mô hình machine learning hay dashboard lâm sàng.
Bản đầu tiên sẽ có
1. Kiểm tra cấu trúc và tính toàn vẹn dữ liệu.
2. Ghi nhận nguồn dữ liệu, số lượng file và checksum.
3. Nạp metadata và bảng mã SCP vào PostgreSQL.
4. Làm sạch và chuẩn hóa bằng SQL/dbt.
5. Tạo mô hình kho dữ liệu dạng star schema.
6. Viết các truy vấn phân tích mẫu.
7. Viết README giải thích cách chạy và các quyết định thiết kế.
Tín hiệu ECG nhị phân vẫn nằm trong các thư mục file. Kho dữ liệu sẽ lưu đường dẫn và thông tin tham chiếu, không nhét toàn bộ mảng sóng vào bảng quan hệ.
4. Luồng dữ liệu dự kiến
PTB-XL gốc
   │
   ├── Metadata CSV
   ├── SCP statements CSV
   └── Tín hiệu WFDB (.hea/.dat)
          │
          ▼
Bronze: bản sao nguồn + manifest + kiểm tra checksum
          │
          ▼
Staging: dữ liệu CSV được nạp vào PostgreSQL
          │
          ▼
Silver: kiểu dữ liệu và giá trị được chuẩn hóa
          │
          ▼
Gold: fact và dimension phục vụ phân tích
Bronze lưu dấu vết nguồn dữ liệu. Staging là lớp nạp gần với cấu trúc nguồn. Silver xử lý kiểu dữ liệu, giá trị thiếu và các chuẩn hóa có căn cứ. Gold chứa các bảng phân tích ổn định hơn.
5. Mô hình kho dữ liệu dự kiến
Có thể điều chỉnh sau khi kiểm tra cột và quan hệ thực tế.
- dim_patient: mã bệnh nhân và thuộc tính nhân khẩu học được phép dùng.
- dim_diagnosis_code: mã SCP và mô tả/nhóm mã.
- dim_recording: thông tin lần ghi ECG, ngày ghi, thiết bị hoặc site nếu phù hợp.
- fact_ecg_record: một dòng cho mỗi lần ghi ECG, chứa khóa liên kết, cờ chất lượng và đường dẫn tới tín hiệu.
- Bảng bridge giữa ECG và mã SCP: một ECG có thể có nhiều mã chẩn đoán được ghi nhận.
ecg_id và patient_id có ý nghĩa khác nhau: một bệnh nhân có thể có nhiều lần ghi ECG. Mô hình cần giữ riêng hai khái niệm đó.
6. Công cụ
Đã có trên máy
- Python 3.13.7
- Git 2.51.0
- VS Code 1.139.1
- AWS CLI 2.37.8
- Môi trường Python .venv đã tạo trong D:\DE_Starter
- Đã cài và kiểm tra import được pandas, wfdb, pyarrow
Dự kiến dùng sau
- PostgreSQL làm kho dữ liệu cục bộ.
- dbt để tổ chức và kiểm thử các phép biến đổi SQL.
- Docker Desktop/WSL2 để chạy PostgreSQL bằng container, nếu máy đáp ứng yêu cầu.
Airflow và Metabase là phần mở rộng sau khi pipeline thủ công chạy đúng. Không cần cài tất cả công cụ ngay từ đầu.
7. GitHub và dữ liệu
Mã nguồn dự án nên được quản lý bằng Git và đẩy lên repo GitHub. Không đưa dataset, .venv, mật khẩu hay khóa API vào repo.
Repo sẽ cần .gitignore để loại trừ ít nhất:
.venv/
data/
*.zip
.env
__pycache__/
Nếu muốn người khác tái tạo dự án, README sẽ hướng dẫn họ tải PTB-XL từ nguồn chính thức và đặt dữ liệu vào vị trí được quy định. README cũng cần ghi nguồn và thông tin license/attribution theo file LICENSE.txt đi kèm dataset.
8. Thứ tự triển khai
1. Mở đúng thư mục dự án D:\DE_Starter trong VS Code.
2. Tạo repo GitHub trống và kết nối Git.
3. Thêm .gitignore để không đẩy dataset và môi trường Python lên GitHub.
4. Tạo README khung và cấu trúc thư mục mã nguồn.
5. Viết chương trình kiểm tra dataset: số dòng, cột thiếu, đường dẫn tín hiệu có tồn tại không.
6. Tạo manifest nguồn và xác minh checksum.
7. Thiết kế schema PostgreSQL.
8. Viết pipeline nạp CSV theo cách chạy lại an toàn.
9. Tạo mô hình staging, silver và gold bằng dbt.
10. Thêm kiểm tra chất lượng dữ liệu và truy vấn phân tích.
11. Viết hướng dẫn chạy từ đầu để người khác có thể tái tạo dự án.