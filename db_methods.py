import sqlite3
from sqlite3 import Error

dbConn = sqlite3.connect("dbtest.db")
dbCurs = dbConn.cursor()

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
known_analytes = [
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
  ("PHO", "Phosphate", "mmol/L"),
  ("DEMO","DEMO - DELETE", "DEMO")
]

def initialiseTables():
  try: 
    dbCurs.executescript(define_tables)
    dbConn.commit()
  except Error as e:
	  print("ERROR [db_methods.initialiseTables]: ", e)

def initialiseAnalytes():
  sql_insert_analytes = """
    INSERT OR IGNORE INTO analyte (code, descriptor, units) VALUES (?, ?, ?);
  """

  try:
    dbCurs.executemany(sql_insert_analytes, known_analytes)
    dbConn.commit() 
    print("Inserted new analyte(s): ", dbCurs.rowcount)
  except Error as e:
    print("ERROR [db_methods.initialiseAnalytes]: ", e)

def selectPatientCount(id=None):
  try:
    dbCurs.execute("""SELECT COUNT(study_id) FROM patient WHERE study_id=?;""", [id])
    rows = dbCurs.fetchall()
    for row in rows:
      return row[0]
  except Error as e:
    print("ERROR [db_methods.selectPatientCount]: ", e)

def insertNewPatient(study_id, date_of_birth, sex=1, ethnicity=0):
  sql_insert_patient = """
    INSERT OR REPLACE INTO patient (study_id, date_of_birth, sex, ethnicity) VALUES (?, ?, ?, ?);
  """

  try:
    dbCurs.execute(sql_insert_patient, (study_id, date_of_birth, sex, ethnicity))
    dbConn.commit() 
    print("Inserted/updated patient: ", dbCurs.rowcount)
  except Error as e:
    print("ERROR [db_methods.insertNewPatient]: ", e)

def insertNewSample(sample_id, receipt_date, sample_type, patient_id):
  sql_insert_sample = """
    INSERT INTO sample (samp_id_full, receipt_date, type) VALUES (?, ?, ?);
  """
  sql_insert_ptsamplink = """
    INSERT INTO patient_sample (study_id, samp_key) VALUES (?, ?);
  """

  try:
    dbCurs.execute(sql_insert_sample, (sample_id, receipt_date, sample_type))
    dbCurs.execute(sql_insert_ptsamplink, (patient_id, sample_id))
    dbConn.commit() 
    print("Inserted sample, created patient link: ", dbCurs.rowcount)
  except Error as e:
    print("ERROR [db_methods.insertNewSample]: ", e)

def selectAnalyteParameters(a_code=None):
  try:
    dbCurs.execute("""SELECT id, code, descriptor, units FROM analyte WHERE code=?;""", [a_code])
    rows = dbCurs.fetchall()
    print (rows)
  except Error as e:
    print("ERROR [db_methods.selectAnalyteParameters]: ", e)

def insertNewResult(samp_id, analyte_id, analyte_result):
  sql_insert_result = """
    INSERT INTO result (analyte_id, value) VALUES (?, ?);
  """
  sql_insert_sampresultlink = """
    INSERT INTO sample_result (samp_key, result_id) VALUES (?, ?);
  """

  try:
    print(dbCurs.execute(sql_insert_result, (analyte_id, analyte_result)))
  except Error as e:
    print ("ERROR [db_methods.insertNewResult]: ", e)

def resetDatabase():
  sql_bobby_tables = """
    DROP TABLE IF EXISTS patient;
    DROP TABLE IF EXISTS sample;
    DROP TABLE IF EXISTS analyte;
    DROP TABLE IF EXISTS result;
    DROP TABLE IF EXISTS patient_sample;
    DROP TABLE IF EXISTS sample_result;
  """
  try:
    dbCurs.executescript(sql_bobby_tables)
    print("Tables deleted")
    initialiseTables()
    print("Tables created")
    initialiseAnalytes()
    print("Analytes added")
  except Error as e:
    print("Error deleting tables, ", e)

def initialise():
  initialiseTables()
  initialiseAnalytes()
  print("RUNNING IN STANDALONE MODE - db_methods.py")
  try:
    dbCurs.execute("""SELECT * FROM analyte;""")
    rows = dbCurs.fetchall()
    for row in rows:
  	  print(row)
  except Error as e:
    print("initialise() Error: ", e)
  dbConn.close()

if __name__ == "__main__":
  initialise()
  #resetDatabase()
