BEGIN;

CREATE TABLE IF NOT EXISTS staging.stg_ecg (
    ecg_id INTEGER PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    age_source NUMERIC,
    age_years NUMERIC,
    age_90_plus BOOLEAN NOT NULL,
    sex_code SMALLINT,
    sex_label TEXT,
    height_cm NUMERIC,
    weight_kg NUMERIC,
    recording_date TIMESTAMP,
    strat_fold SMALLINT,
    filename_lr TEXT,
    filename_hr TEXT,
    source_file TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.bridge_ecg_scp (
    ecg_id INTEGER NOT NULL
        REFERENCES staging.stg_ecg (ecg_id),
    scp_code TEXT NOT NULL
        REFERENCES raw.ptbxl_scp_statement_source (scp_code),
    likelihood NUMERIC,
    PRIMARY KEY (ecg_id, scp_code)
);

TRUNCATE TABLE staging.bridge_ecg_scp, staging.stg_ecg;

INSERT INTO staging.stg_ecg (
    ecg_id,
    patient_id,
    age_source,
    age_years,
    age_90_plus,
    sex_code,
    sex_label,
    height_cm,
    weight_kg,
    recording_date,
    strat_fold,
    filename_lr,
    filename_hr,
    source_file,
    dataset_version,
    loaded_at
)
SELECT
    ecg_id,
    patient_id::BIGINT,
    age,
    CASE WHEN age >= 300 THEN NULL ELSE age END,
    COALESCE(age >= 300, FALSE),
    sex,
    CASE sex
        WHEN 0 THEN 'Male'
        WHEN 1 THEN 'Female'
        ELSE 'Unknown'
    END,
    height,
    weight,
    recording_date,
    strat_fold,
    filename_lr,
    filename_hr,
    source_file,
    dataset_version,
    loaded_at
FROM raw.ptbxl_ecg_source;

INSERT INTO staging.bridge_ecg_scp (
    ecg_id,
    scp_code,
    likelihood
)
SELECT
    r.ecg_id,
    match.parts[1],
    match.parts[2]::NUMERIC
FROM raw.ptbxl_ecg_source AS r
CROSS JOIN LATERAL regexp_matches(
    r.scp_codes,
    $$'([^']+)'\s*:\s*([0-9]+[.]?[0-9]*)$$,
    'g'
) AS match(parts);

COMMIT;