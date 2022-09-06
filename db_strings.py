# SQL STRINGS
# abstracted to make it clearer when editing dbmethods. Various selects to get specific data, added as necessary
# - PATIENT strings
# - SAMPLE strings
# - RESULT strings
# - ANALYTE string(s?)
# - LINEAR REGRESSION strings

# Version 2 schema removes most/all link tables for ease of programming simple queries for quick answers
# it was such a pain finding the right combination and order of JOIN statements to perform individual tasks
# v2 is just patient, sample (with patient ID), result (with sample ID), no foreign keys or linked lists
# I know its not the "correct" way, but for a personal project and a simple database, its sufficient.
define_tables = """
  CREATE TABLE IF NOT EXISTS patient (
    study_id INTEGER PRIMARY KEY,
    date_of_birth TEXT NOT NULL,
    sex INTEGER DEFAULT 1,
    original_file TEXT NOT NULL,
    date_added TEXT NOT NULL
  );
  
  CREATE TABLE IF NOT EXISTS sample (
    samp_key INTEGER PRIMARY KEY AUTOINCREMENT,
    samp_id_full TEXT UNIQUE,
    study_id INTEGER,
    receipt_date TEXT NOT NULL,
    type INTEGER DEFAULT 1,
    location TEXT NOT NULL,
    category TEXT NOT NULL,
    original_file TEXT NOT NULL,
    date_added TEXT NOT NULL
  );
    
  CREATE TABLE IF NOT EXISTS analyte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    descriptor TEXT NOT NULL,
    units TEXT NOT NULL
  );
  
  CREATE TABLE IF NOT EXISTS result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    samp_key INTEGER,
    analyte_id INTEGER,
    value TEXT,
    comment TEXT,
    original_file TEXT NOT NULL,
    date_added TEXT NOT NULL
  );
  
  CREATE TABLE IF NOT EXISTS linear_regression_ordinaldate (
    study_id INTEGER,
    samples_hash TEXT NOT NULL,
    date_updated TEXT NOT NULL,
    sample_count INTEGER,
    slope REAL,
    intercept REAL,
    r REAL,
    p REAL,
    std_err REAL,
    PRIMARY KEY (study_id, samples_hash),
    FOREIGN KEY (study_id) REFERENCES patient (study_id) ON DELETE CASCADE ON UPDATE NO ACTION
  )
"""

# Five tables, five insert statements
# Using SQLite's data sanitation to prevent errors from CSV imports
insert_analytes = """INSERT OR IGNORE INTO analyte (code, descriptor, units) VALUES (?, ?, ?);"""
insert_patient = """INSERT OR REPLACE INTO patient (study_id, date_of_birth, sex, original_file, date_added) VALUES (?, ?, ?, ?, ?);"""
insert_sample = """INSERT INTO sample (samp_id_full, study_id, receipt_date, type, location, category, original_file, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
insert_result = """INSERT INTO result (samp_key, analyte_id, value, original_file, date_added) VALUES (?, ?, ?, ?, ?);"""
insert_linearregression = """INSERT INTO linear_regression_ordinaldate (study_id, samples_hash, date_updated, sample_count, slope, intercept, r, p, std_err) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

# https://xkcd.com/327/
# Personal preference to drop tables individually.
bobby_tables = """
  DROP TABLE IF EXISTS patient;
  DROP TABLE IF EXISTS sample;
  DROP TABLE IF EXISTS analyte;
  DROP TABLE IF EXISTS result;
  DROP TABLE IF EXISTS linear_regression_ordinaldate;
"""


# PATIENT strings
# Default select full record on one patient by their study_id
select_patient_by_id = """SELECT study_id, date_of_birth, sex, original_file, date_added FROM patient WHERE study_id = ?;"""
# Useful select to view all patients imported from a specific file / verify numbers etc
select_patients_by_original_file = """SELECT study_id, date_of_birth, sex, original_file, date_added FROM patient WHERE original_file = ?;"""
# Select patient IDs but from the sample table, when they have more than n samples attributed to their study_id
# need this for reducing number of records to process with linear regression
select_patient_id_if_multiple_samples = """SELECT study_id FROM sample GROUP BY study_id HAVING count(*) > ?;"""


# SAMPLE strings
# -- Try to JOIN with patient table where possible to maintain patient-sample association
# Default select full record on one sample by the sample ID from TelePath
select_sample_by_full_id = """SELECT s.samp_key, s.samp_id_full, s.receipt_date, s.type, s.location, s.category, s.original_file, s.date_added, p.study_id, p.date_of_birth, p.sex, p.original_file, p.date_added FROM sample s JOIN patient p ON (s.study_id = p.study_id) WHERE samp_id_full LIKE ?;"""
# Used to verify csv parser imported expected number of samples 
select_samples_by_original_file = """SELECT s.samp_key, s.samp_id_full, s.receipt_date, s.type, s.location, s.category, s.original_file, s.date_added, p.study_id, p.date_of_birth, p.sex, p.original_file, p.date_added FROM sample s JOIN patient p ON (s.study_id = p.study_id) WHERE s.original_file = ?;"""

# RESULT strings
select_results_by_samp_key = """SELECT id, samp_key, analyte_id, value, comment, original_file, date_added FROM result WHERE samp_key = ?;"""
select_results_expanded_by_samp_key = """SELECT id, samp_key, analyte_id, !!!!!!!!!!, value, comment, original_file, date_added FROM result WHERE samp_key = ?;"""

# ANALYTE string (should only need the one)
select_analyte_by_code = """SELECT id, code, descriptor, units FROM analyte WHERE code = ?;"""