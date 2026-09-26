-- One facility-condition row per hospital. :region = 'US' includes Indiana.
-- :minimum = 0 means no volume filter. Missing volume then remains eligible.
-- Volume filters are analyst sensitivity settings, not CMS eligibility rules.
WITH population AS (
    SELECT r.*,
        CASE
          WHEN err IS NULL THEN 'missing_ratio'
          WHEN :minimum > 0 AND discharges IS NULL THEN 'missing_volume'
          WHEN :minimum > 0 AND discharges < :minimum THEN 'below_volume'
          ELSE 'eligible'
        END AS disposition
    FROM result r
    JOIN facility f USING (facility_id)
    WHERE measure_id = :measure
      AND (:region = 'US' OR f.state = :region)
), ordered AS (
    SELECT err,
           ROW_NUMBER() OVER (ORDER BY err, facility_id) AS position,
           COUNT(*) OVER () AS n
    FROM population WHERE disposition = 'eligible'
), median_value AS (
    SELECT AVG(err) AS median_err FROM ordered
    WHERE position IN ((n + 1) / 2, (n + 2) / 2)
)
SELECT COUNT(*) AS source_hospitals,
       COUNT(CASE WHEN disposition = 'eligible' THEN 1 END) AS eligible,
       COUNT(CASE WHEN disposition = 'missing_ratio' THEN 1 END) AS missing_ratio,
       COUNT(CASE WHEN disposition = 'missing_volume' THEN 1 END) AS missing_volume,
       COUNT(CASE WHEN disposition = 'below_volume' THEN 1 END) AS below_volume,
       COUNT(CASE WHEN disposition = 'eligible' AND err > 1 THEN 1 END) AS above_one,
       COUNT(CASE WHEN disposition = 'eligible' AND err = 1 THEN 1 END) AS exactly_one,
       COUNT(CASE WHEN disposition = 'eligible' AND err < 1 THEN 1 END) AS below_one,
       (SELECT median_err FROM median_value) AS median_err,
       1.0 * COUNT(CASE WHEN disposition = 'eligible' AND err > 1 THEN 1 END)
         / NULLIF(COUNT(CASE WHEN disposition = 'eligible' THEN 1 END), 0) AS above_share
FROM population;
