BEGIN;

CREATE TABLE IF NOT EXISTS mart.dim_patient (
    patient_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id BIGINT NOT NULL UNIQUE,
    sex_code SMALLINT,
    sex_label TEXT
);

CREATE TABLE IF NOT EXISTS mart.dim_scp_statement (
    scp_code TEXT PRIMARY KEY,
    description TEXT,
    is_diagnostic SMALLINT,
    is_form SMALLINT,
    is_rhythm SMALLINT,
    diagnostic_class TEXT,
    diagnostic_subclass TEXT,
    statement_category TEXT,
    scp_ecg_statement_description TEXT,
    aha_code TEXT,
    aecg_refid TEXT,
    cdisc_code TEXT,
    dicom_code TEXT
);

CREATE TABLE IF NOT EXISTS mart.fact_ecg_recording (
    ecg_id INTEGER PRIMARY KEY,
    patient_key BIGINT NOT NULL
        REFERENCES mart.dim_patient (patient_key),
    age_at_recording NUMERIC,
    age_90_plus BOOLEAN NOT NULL,
    height_cm NUMERIC,
    weight_kg NUMERIC,
    recording_date TIMESTAMP,
    strat_fold SMALLINT,
    filename_lr TEXT,
    filename_hr TEXT,
    dataset_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mart.fact_ecg_scp (
    ecg_id INTEGER NOT NULL
        REFERENCES mart.fact_ecg_recording (ecg_id),
    scp_code TEXT NOT NULL
        REFERENCES mart.dim_scp_statement (scp_code),
    likelihood NUMERIC NOT NULL,
    PRIMARY KEY (ecg_id, scp_code)
);

TRUNCATE TABLE
    mart.fact_ecg_scp,
    mart.fact_ecg_recording,
    mart.dim_scp_statement,
    mart.dim_patient
RESTART IDENTITY;

INSERT INTO mart.dim_patient (
    patient_id,
    sex_code,
    sex_label
)
SELECT DISTINCT
    patient_id,
    sex_code,
    sex_label
FROM staging.stg_ecg;

INSERT INTO mart.dim_scp_statement (
    scp_code,
    description,
    is_diagnostic,
    is_form,
    is_rhythm,
    diagnostic_class,
    diagnostic_subclass,
    statement_category,
    scp_ecg_statement_description,
    aha_code,
    aecg_refid,
    cdisc_code,
    dicom_code
)
SELECT
    scp_code,
    description,
    diagnostic,
    form,
    rhythm,
    diagnostic_class,
    diagnostic_subclass,
    statement_category,
    scp_ecg_statement_description,
    aha_code,
    aecg_refid,
    cdisc_code,
    dicom_code
FROM raw.ptbxl_scp_statement_source;

INSERT INTO mart.fact_ecg_recording (
    ecg_id,
    patient_key,
    age_at_recording,
    age_90_plus,
    height_cm,
    weight_kg,
    recording_date,
    strat_fold,
    filename_lr,
    filename_hr,
    dataset_version
)
SELECT
    e.ecg_id,
    p.patient_key,
    e.age_years,
    e.age_90_plus,
    e.height_cm,
    e.weight_kg,
    e.recording_date,
    e.strat_fold,
    e.filename_lr,
    e.filename_hr,
    e.dataset_version
FROM staging.stg_ecg AS e
JOIN mart.dim_patient AS p
    ON p.patient_id = e.patient_id;

INSERT INTO mart.fact_ecg_scp (
    ecg_id,
    scp_code,
    likelihood
)
SELECT
    ecg_id,
    scp_code,
    likelihood
FROM staging.bridge_ecg_scp;

COMMIT;

SELECT 'dim_patient' AS table_name, COUNT(*) AS row_count
FROM mart.dim_patient
UNION ALL
SELECT 'dim_scp_statement', COUNT(*)
FROM mart.dim_scp_statement
UNION ALL
SELECT 'fact_ecg_recording', COUNT(*)
FROM mart.fact_ecg_recording
UNION ALL
SELECT 'fact_ecg_scp', COUNT(*)
FROM mart.fact_ecg_scp
ORDER BY table_name;