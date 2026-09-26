PRAGMA foreign_keys = ON;
CREATE TABLE facility (
    facility_id TEXT PRIMARY KEY,
    facility_name TEXT NOT NULL,
    state TEXT NOT NULL
);
CREATE TABLE measure (
    measure_id TEXT PRIMARY KEY,
    label TEXT NOT NULL
);
CREATE TABLE result (
    facility_id TEXT REFERENCES facility(facility_id),
    measure_id TEXT REFERENCES measure(measure_id),
    discharges INTEGER,
    err REAL,
    predicted_rate REAL,
    expected_rate REAL,
    discharges_raw TEXT NOT NULL,
    err_raw TEXT NOT NULL,
    readmissions_raw TEXT NOT NULL,
    footnote TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    PRIMARY KEY (facility_id, measure_id),
    CHECK (err IS NULL OR err > 0),
    CHECK (discharges IS NULL OR discharges >= 0)
);
