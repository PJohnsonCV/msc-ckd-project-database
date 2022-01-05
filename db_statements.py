define_tables = """
  CREATE TABLE IF NOT EXISTS patient (
    study_id INTEGER PRIMARY KEY,
    date_of_birth TEXT NOT NULL,
    sex INTEGER DEFAULT 1,
    ethnicity INTEGER DEFAULT 0
  );
  
  CREATE TABLE IF NOT EXISTS sample (
    samp_key INTEGER PRIMARY KEY AUTOINCREMENT,
    samp_id_full TEXT UNIQUE,
    receipt_date TEXT NOT NULL,
    type INTEGER DEFAULT 1
  );
  
  CREATE TABLE IF NOT EXISTS patient_sample (
    study_id INTEGER,
    samp_key INTEGER,
    PRIMARY KEY (study_id, samp_key),
    FOREIGN KEY (study_id) REFERENCES patient (study_id) ON DELETE CASCADE ON UPDATE NO ACTION,
    FOREIGN KEY (samp_key) REFERENCES sample (samp_key) ON DELETE CASCADE ON UPDATE NO ACTION
  );
  
  CREATE TABLE IF NOT EXISTS analyte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    descriptor TEXT NOT NULL,
    units TEXT NOT NULL
  );
  
  CREATE TABLE IF NOT EXISTS result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analyte_id INTEGER,
    value TEXT,
    comment TEXT,
    FOREIGN KEY (analyte_id) REFERENCES analyte (id)
  );
  
  CREATE TABLE IF NOT EXISTS sample_result (
    samp_key INTEGER,
    result_id INTEGER,
    PRIMARY KEY (samp_key, result_id),
    FOREIGN KEY (samp_key) REFERENCES sample (samp_key) ON DELETE CASCADE ON UPDATE NO ACTION,
    FOREIGN KEY (samp_key) REFERENCES result (id) ON DELETE CASCADE ON UPDATE NO ACTION
  );
"""
insert_analytes = """
  INSERT OR IGNORE INTO analyte (code, descriptor, units) VALUES (?, ?, ?);
"""
insert_patient = """
  INSERT OR REPLACE INTO patient (study_id, date_of_birth, sex, ethnicity) VALUES (?, ?, ?, ?);
"""
insert_sample = """
 INSERT INTO sample (samp_id_full, receipt_date, type) VALUES (?, ?, ?);
"""
insert_ptsamplink = """
  INSERT INTO patient_sample (study_id, samp_key) VALUES (?, ?);
"""
insert_result = """
  INSERT INTO result (analyte_id, value) VALUES (?, ?);
"""
insert_sampresultlink = """
  INSERT INTO sample_result (samp_key, result_id) VALUES (?, ?);
"""
bobby_tables = """
  DROP TABLE IF EXISTS patient;
  DROP TABLE IF EXISTS sample;
  DROP TABLE IF EXISTS analyte;
  DROP TABLE IF EXISTS result;
  DROP TABLE IF EXISTS patient_sample;
  DROP TABLE IF EXISTS sample_result;
"""