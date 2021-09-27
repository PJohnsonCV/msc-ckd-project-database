import sqlite3
from sqlite3 import Error

dbConn = sqlite3.connect("dbtest.db") #(":memory:") #"/mnt/chromeos/MyFiles/Downloads/rawdata.db")
dbCurs = dbConn.cursor()

defineTables = """
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
defineAnalytes = """
    INSERT INTO analyte (code, descriptor, units) VALUES (?, ?, ?);
"""
knownAnalytes = [
  ("SOD", "Sodium", "mmol/L"),
  ("POT", "Potassium", "mmol/L"),
  ("URE", "Urea", "mmol/L"),
  ("CRE", "Creatinine", "umol/L"),
  ("GFR", "eGFR (old/U&E)", "mL/min/1.73m^2"),
  ("GFRE", "eGFR", "mL/min/1.73m^2"),
  ("AKI", "AKI", "(score)"),
  ("UMICR", "Albumin Ratio", "mg/mmol"),
  ("CRP", "C.Reactive Protein", "mg/L"),
  ("IHBA1C", "HbA1c", "mmol/mo"),
  ("HB", "Haemoglobin", "g/L"),
  ("HCT", "Haematocrit", "L/L"),
  ("MCH", "Mean cell haemoglobin", "pg"),
  ("PHO", "Phosphate", "mmol/L")
]

#dbCurs.execute("""DELETE FROM analyte WHERE code != "TEST";""")

try: 
  dbCurs.executescript(defineTables)
  dbCurs.executemany(defineAnalytes, knownAnalytes) 
  print("Inserted: ", dbCurs.rowcount)
  dbConn.commit()
except Error as e:
	print(e)


dbCurs.execute("""SELECT * FROM analyte;""")
rows = dbCurs.fetchall()
for row in rows:
	  print(row)
dbConn.close()
