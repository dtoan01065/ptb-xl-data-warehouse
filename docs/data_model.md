# PTB-XL Data Warehouse — Data Model v0.1

## Mục tiêu

Xây dựng kho dữ liệu phục vụ quản lý, kiểm tra và phân tích metadata của PTB-XL.
Dự án không dùng để chẩn đoán hoặc đưa ra khuyến nghị y tế.

## Nguồn dữ liệu

- Dataset: PTB-XL, phiên bản 1.0.3
- Metadata ECG: `ptbxl_database.csv`
- Từ điển statement: `scp_statements.csv`
- Tín hiệu: WFDB trong `records100/` và `records500/`
- Dữ liệu gốc nằm ngoài GitHub trong `data/`

## Grain — ý nghĩa của một dòng

- `ptbxl_database.csv`: một dòng cho một lần ghi ECG; khóa nguồn là `ecg_id`.
- `patient_id`: định danh bệnh nhân; một bệnh nhân có thể có nhiều ECG.
- Bảng liên kết ECG–SCP: một dòng cho một cặp `(ecg_id, scp_code)`.
- `scp_statements.csv`: một dòng cho một mã SCP.

## Các lớp dữ liệu

### Raw

- `raw.ptbxl_ecg_source`: bản nạp theo cấu trúc nguồn của `ptbxl_database.csv`.
- `raw.scp_statement_source`: bản nạp theo cấu trúc nguồn của `scp_statements.csv`.

Giữ lại dữ liệu nguồn để có thể đối chiếu khi quy tắc xử lý thay đổi.

### Staging

- `staging.ecg_record`: một dòng cho mỗi `ecg_id`; chuẩn hóa kiểu dữ liệu nhưng giữ các trường nguồn.
- `staging.ecg_scp_statement`: tách `scp_codes` thành nhiều dòng, giữ nguyên mã và giá trị likelihood nguồn.

### Mart

- `mart.dim_patient`: một dòng cho mỗi `patient_id`; gồm mã bệnh nhân và giới tính nguồn đã kiểm tra tính nhất quán.
- `mart.dim_scp_statement`: từ điển mã SCP, mô tả, nhóm và phân cấp.
- `mart.fact_ecg_record`: một dòng cho mỗi ECG; liên kết bệnh nhân và lưu thông tin lần ghi.
- `mart.bridge_ecg_scp_statement`: nối ECG với nhiều statement SCP.

## Quy tắc xử lý đã biết

- Giữ `age` gốc. Giá trị 300 là mã hóa cho tuổi từ 90 trở lên, không phải tuổi thật.
- Tạo cờ `age_is_90_plus`; tuổi dùng cho thống kê thông thường để trống khi tuổi gốc bằng 300.
- Giữ mã giới tính nguồn; ánh xạ 0 = nam và 1 = nữ.
- Giữ likelihood của SCP đúng theo nguồn; không diễn giải thành xác suất đã hiệu chuẩn.
- Một ECG có thể có nhiều statement; các nhóm mã không loại trừ lẫn nhau.
- Ngày ghi đã được dịch theo từng bệnh nhân; giữ lại để truy xuất nhưng không dùng kết luận xu hướng thời gian giữa bệnh nhân.
- `filename_lr` và `filename_hr` là đường dẫn tương đối tới tín hiệu WFDB; không lưu waveform trong bảng PostgreSQL.
- Giá trị thiếu là chưa biết/chưa được ghi nhận, không tự đổi thành false hoặc 0.

## Kiểm tra dữ liệu đã chạy

- 21.799 ECG; 18.869 bệnh nhân.
- `ecg_id` không trùng; `patient_id` không thiếu.
- 21.799/21.799 cặp `.hea` và `.dat` ở 100 Hz tồn tại.
- 21.799/21.799 cặp `.hea` và `.dat` ở 500 Hz tồn tại.
- Header mẫu ở cả hai tần số có 12 đạo trình và dài 10 giây.
- 87.203 file khớp SHA-256 trong manifest đi kèm.
- 71/71 mã SCP trong metadata có trong từ điển.
- Giới tính nhất quán theo `patient_id`, không thiếu trong metadata.