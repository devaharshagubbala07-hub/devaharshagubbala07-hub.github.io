PRAGMA foreign_keys = ON;
CREATE TABLE patient (
    patient_id TEXT PRIMARY KEY,
    gender TEXT,
    birth_date TEXT -- preserve YYYY / YYYY-MM / YYYY-MM-DD or NULL
);
CREATE TABLE observation (
    observation_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES patient(patient_id),
    status TEXT NOT NULL,
    effective_timestamp TEXT NOT NULL,
    heart_rate_per_min REAL NOT NULL
);
CREATE TABLE condition_record (
    condition_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES patient(patient_id),
    code_system TEXT NOT NULL,
    code TEXT NOT NULL
);
CREATE TABLE audit (
    entry_number INTEGER PRIMARY KEY,
    resource_type TEXT,
    resource_key TEXT,
    disposition TEXT NOT NULL,
    reasons TEXT
);
