-- Demo record coverage, not a clinical quality measure.
-- Exactly 'final' is the stated reporting rule; amended/corrected are not included.
WITH patient_coverage AS (
    SELECT p.patient_id,
           COUNT(o.observation_id) AS final_observation_rows
    FROM patient p
    LEFT JOIN observation o
      ON p.patient_id = o.patient_id AND o.status = 'final'
    GROUP BY p.patient_id
)
SELECT COUNT(*) AS patients,
       COALESCE(SUM(final_observation_rows > 0), 0) AS with_final_observation,
       COALESCE(SUM(final_observation_rows = 0), 0) AS without_final_observation,
       COALESCE(SUM(final_observation_rows), 0) AS final_observation_rows
FROM patient_coverage;
