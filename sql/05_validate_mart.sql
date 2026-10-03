WITH checks AS (
    SELECT
        'Patient dimension matches staging' AS check_name,
        (
            SELECT COUNT(DISTINCT patient_id)
            FROM staging.stg_ecg
        )::TEXT AS actual,
        (
            SELECT COUNT(*)
            FROM mart.dim_patient
        )::TEXT AS expected

    UNION ALL

    SELECT
        'ECG fact rows match staging',
        (SELECT COUNT(*)::TEXT FROM mart.fact_ecg_recording),
        (SELECT COUNT(*)::TEXT FROM staging.stg_ecg)

    UNION ALL

    SELECT
        'Unique ECG IDs in fact',
        (
            SELECT COUNT(DISTINCT ecg_id)::TEXT
            FROM mart.fact_ecg_recording
        ),
        (
            SELECT COUNT(*)::TEXT
            FROM mart.fact_ecg_recording
        )

    UNION ALL

    SELECT
        'ECG-SCP fact rows match staging',
        (SELECT COUNT(*)::TEXT FROM mart.fact_ecg_scp),
        (SELECT COUNT(*)::TEXT FROM staging.bridge_ecg_scp)

    UNION ALL

    SELECT
        'Unique ECG-SCP pairs in mart',
        (
            SELECT COUNT(DISTINCT (ecg_id, scp_code))::TEXT
            FROM mart.fact_ecg_scp
        ),
        (
            SELECT COUNT(*)::TEXT
            FROM mart.fact_ecg_scp
        )

    UNION ALL

    SELECT
        'Age sentinel rows preserved',
        (
            SELECT COUNT(*)::TEXT
            FROM mart.fact_ecg_recording
            WHERE age_90_plus
        ),
        '293'

    UNION ALL

    SELECT
        'Sentinel 300 incorrectly stored as age',
        (
            SELECT COUNT(*)::TEXT
            FROM mart.fact_ecg_recording
            WHERE age_90_plus
              AND age_at_recording IS NOT NULL
        ),
        '0'

    UNION ALL

    SELECT
        'SCP dimension matches source dictionary',
        (SELECT COUNT(*)::TEXT FROM mart.dim_scp_statement),
        (
            SELECT COUNT(*)::TEXT
            FROM raw.ptbxl_scp_statement_source
        )
)
SELECT
    check_name,
    actual,
    expected,
    actual = expected AS passed
FROM checks
ORDER BY check_name;