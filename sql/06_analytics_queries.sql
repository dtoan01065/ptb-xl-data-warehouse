-- 1. Các mã SCP chẩn đoán phổ biến nhất
SELECT
    s.scp_code,
    s.description,
    s.diagnostic_class,
    COUNT(DISTINCT f.ecg_id) AS ecg_count,
    COUNT(DISTINCT p.patient_id) AS patient_count,
    ROUND(AVG(b.likelihood), 2) AS avg_source_likelihood
FROM mart.fact_ecg_scp AS b
JOIN mart.fact_ecg_recording AS f
    ON f.ecg_id = b.ecg_id
JOIN mart.dim_patient AS p
    ON p.patient_key = f.patient_key
JOIN mart.dim_scp_statement AS s
    ON s.scp_code = b.scp_code
WHERE s.is_diagnostic = 1
GROUP BY s.scp_code, s.description, s.diagnostic_class
ORDER BY ecg_count DESC, s.scp_code
LIMIT 20;


-- 2. Phân bố ECG theo nhóm chẩn đoán
SELECT
    s.diagnostic_class,
    COUNT(DISTINCT f.ecg_id) AS ecg_count,
    COUNT(DISTINCT p.patient_id) AS patient_count,
    ROUND(
        COUNT(DISTINCT f.ecg_id) * 100.0
        / NULLIF((SELECT COUNT(*) FROM mart.fact_ecg_recording), 0),
        2
    ) AS pct_of_all_ecgs
FROM mart.fact_ecg_scp AS b
JOIN mart.fact_ecg_recording AS f
    ON f.ecg_id = b.ecg_id
JOIN mart.dim_patient AS p
    ON p.patient_key = f.patient_key
JOIN mart.dim_scp_statement AS s
    ON s.scp_code = b.scp_code
WHERE s.is_diagnostic = 1
  AND s.diagnostic_class IS NOT NULL
GROUP BY s.diagnostic_class
ORDER BY ecg_count DESC;


-- 3. Số ECG theo nhóm tuổi và giới tính
WITH classified AS (
    SELECT
        CASE
            WHEN f.age_90_plus THEN '90+'
            WHEN f.age_at_recording IS NULL THEN 'Unknown'
            WHEN f.age_at_recording < 18 THEN '<18'
            WHEN f.age_at_recording < 40 THEN '18-39'
            WHEN f.age_at_recording < 60 THEN '40-59'
            WHEN f.age_at_recording < 75 THEN '60-74'
            ELSE '75-89'
        END AS age_band,
        CASE
            WHEN f.age_90_plus THEN 6
            WHEN f.age_at_recording IS NULL THEN 7
            WHEN f.age_at_recording < 18 THEN 1
            WHEN f.age_at_recording < 40 THEN 2
            WHEN f.age_at_recording < 60 THEN 3
            WHEN f.age_at_recording < 75 THEN 4
            ELSE 5
        END AS band_order,
        p.sex_label,
        p.patient_id
    FROM mart.fact_ecg_recording AS f
    JOIN mart.dim_patient AS p
        ON p.patient_key = f.patient_key
)
SELECT
    age_band,
    sex_label,
    COUNT(*) AS ecg_count,
    COUNT(DISTINCT patient_id) AS patient_count
FROM classified
GROUP BY age_band, band_order, sex_label
ORDER BY band_order, sex_label;

-- 4. Mức độ đầy đủ của một số trường trong mart
SELECT
    COUNT(*) AS total_ecgs,
    COUNT(*) FILTER (WHERE age_at_recording IS NOT NULL) AS ecgs_with_age,
    COUNT(*) FILTER (WHERE height_cm IS NOT NULL) AS ecgs_with_height,
    COUNT(*) FILTER (WHERE weight_kg IS NOT NULL) AS ecgs_with_weight,
    COUNT(*) FILTER (WHERE filename_lr IS NOT NULL) AS ecgs_with_100hz_file,
    COUNT(*) FILTER (WHERE filename_hr IS NOT NULL) AS ecgs_with_500hz_file
FROM mart.fact_ecg_recording;


-- 5. Phân bố ECG theo fold có sẵn trong dataset
SELECT
    strat_fold,
    COUNT(*) AS ecg_count,
    COUNT(DISTINCT patient_key) AS patient_count
FROM mart.fact_ecg_recording
GROUP BY strat_fold
ORDER BY strat_fold;