WITH checks AS (
    SELECT
        'ECG rows' AS check_name,
        COUNT(*)::TEXT AS actual,
        '21799' AS expected
    FROM staging.stg_ecg

    UNION ALL

    SELECT
        'Unique ECG IDs',
        COUNT(DISTINCT ecg_id)::TEXT,
        '21799'
    FROM staging.stg_ecg

    UNION ALL

    SELECT
        'Missing patient IDs',
        COUNT(*) FILTER (WHERE patient_id IS NULL)::TEXT,
        '0'
    FROM staging.stg_ecg

    UNION ALL

    SELECT
        'Age 90+ sentinel rows',
        COUNT(*) FILTER (WHERE age_90_plus)::TEXT,
        '293'
    FROM staging.stg_ecg

    UNION ALL

    SELECT
        'Sentinel age incorrectly kept as years',
        COUNT(*) FILTER (
            WHERE age_90_plus AND age_years IS NOT NULL
        )::TEXT,
        '0'
    FROM staging.stg_ecg

    UNION ALL

    SELECT
        'Unknown sex codes',
        COUNT(*) FILTER (
            WHERE sex_code IS NOT NULL
              AND sex_code NOT IN (0, 1)
        )::TEXT,
        '0'
    FROM staging.stg_ecg

    UNION ALL

    SELECT
        'ECG-SCP bridge rows',
        COUNT(*)::TEXT,
        '61007'
    FROM staging.bridge_ecg_scp

    UNION ALL

    SELECT
        'Duplicate ECG-SCP pairs',
        (COUNT(*) - COUNT(DISTINCT (ecg_id, scp_code)))::TEXT,
        '0'
    FROM staging.bridge_ecg_scp

    UNION ALL

    SELECT
        'Null likelihood values',
        COUNT(*) FILTER (WHERE likelihood IS NULL)::TEXT,
        '0'
    FROM staging.bridge_ecg_scp

    UNION ALL

    SELECT
        'Likelihood outside 0-100',
        COUNT(*) FILTER (
            WHERE likelihood < 0 OR likelihood > 100
        )::TEXT,
        '0'
    FROM staging.bridge_ecg_scp

    UNION ALL

    SELECT
        'SCP codes missing from dictionary',
        COUNT(*)::TEXT,
        '0'
    FROM staging.bridge_ecg_scp AS b
    LEFT JOIN raw.ptbxl_scp_statement_source AS s
        ON s.scp_code = b.scp_code
    WHERE s.scp_code IS NULL
)
SELECT
    check_name,
    actual,
    expected,
    actual = expected AS passed
FROM checks
ORDER BY check_name;