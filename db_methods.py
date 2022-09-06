import sqlite3
from sqlite3 import Error
import db_strings as sql
import menus as menu
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(levelname)s | %(message)s', level=logging.DEBUG)

# Default settings for sqlite3 connection and cursor
dbname = "study_data_v2.db" #odg don't overwrite the original
dbConn = sqlite3.connect(dbname)
dbCurs = dbConn.cursor()

# List of analyte tuples: 
# - Code as it is output by TelePath gather
# - Nice name for printing "professionally"
# - Units of the analyte (for printing)
known_analytes = [
  ("Sodium", "Sodium", "mmol/L"),
  ("POT", "Potassium", "mmol/L"),
  ("Urea", "Urea", "mmol/L"),
  ("CRE", "Creatinine", "umol/L"),
  #("GFR", "eGFR (old/U&E)", "mL/min/1.73m^2"),
  ("eGFR", "eGFR", "mL/min/1.73m^2"),
  ("AKI", "AKI", "(score)"),
  ("UMICR", "Albumin Ratio", "mg/mmol"),
  ("CRP", "C.Reactive Protein", "mg/L"),
  ("IHBA1C", "HbA1c", "mmol/mo"),
  ("HbA1c", "HbA1c", "mmol/mo"),
  ("Hb", "Haemoglobin", "g/L"),
  ("HCT", "Haematocrit", "L/L"),
  ("MCH", "Mean cell haemoglobin", "pg"),
  ("PHO", "Phosphate", "mmol/L")
]

# Commits the CREATE TABLE script for all tables in one go
# Returns true on success or false on failure
# Only instance of executescript() in module, no need to refactor
def initialiseTables():
  try: 
    dbCurs.executescript(sql.define_tables)
    logging.info("db_methods.py:initialiseTables Successfully created tables.")
    return True
  except Error as e:
    logging.error("db_methods.py:initialiseTables ", e)
    return False

# Populates the analytes table with the defined list, known_analytes
# Outputs the completion with the number of rows (assumed .rowcount
# is accurate), or the error code as necessary
def initialiseAnalytes():
  try:
    dbCurs.executemany(sql.insert_analytes, known_analytes)
    dbConn.commit() 
    logging.info("db_methods.py:initialiseAnalytes Inserted {} of {} analyte(s)".format(dbCurs.rowcount, len(known_analytes)))
  except Error as e:
    #dbConn.close()
    logging.error("dbmethods.py - ", e)

# Initialisation / reset of database
# Deletes tables if the exist, then creates them 
# Populates the analytes table with default values
# Outputs the row counts for each table to show success/failure
def resetDatabase():
  try:
    dbCurs.executescript(sql.bobby_tables)
    logging.info("db_methods.py - Tables deleted")
    if initialiseTables():
      initialiseAnalytes()
  except Error as e:
    logging.error("db_methods.py:resetDatabase ", e)

# Pass in the required select from db_statements, and appropriate param values
# Not sure why I named this ONE, returns ALL rows from the select, or False if
# an execution error. 
# Minimises code reuse for all the selects used in the module. 
def tryCatchSelect(sql_string, values, method_name):
  try:
    dbCurs.execute(sql_string, values)
    rows = dbCurs.fetchall()
    return rows
  except Error as e:
    logging.debug("tryCatchSelect sql_string [{}], values [{}], method_name [{}]".format(sql_string, values, method_name))
    logging.error("tryCatchSelect:{}, error: ".format(method_name, e))
    return False

# Helper functions help keep things tidy!
def commit():
  dbConn.commit()
  logging.info("Database committed")

def patientSelectByID(pid):
  results = tryCatchSelect(sql.select_patient_by_id, (pid,), "patientSelectByID")
  return results

# Groups study_id having a count greater than n in the sample table, excludes <= n obviously, so good to prevent processing 0 / 1 / 2 samples for linear regression
def patientsSelectSampleCountGreaterThan(count_gt):
  results = tryCatchSelect(sql.select_patient_id_if_multiple_samples, (count_gt,), "patientsSelectSampleCountGreaterThan")

def patientInsertNew(row_number, study_id, date_of_birth, sex=1, file="Manual entry", process_date="2022-09-04"):
  try:
    dbCurs.execute(sql.insert_patient, (study_id, date_of_birth, sex, file, process_date))
  except Error as e:
    logging.error("db_methods.py:patientInsertNew csv row {}: {}".format(row_number, e))

def sampleSelectByIDFull(sid):
  results = tryCatchSelect(sql.select_sample_by_full_id, ("%"+sid+"%",), "sampleSelectByIDFull")
  return results

def sampleInsertNew(row_number, sample_id, patient_id, receipt_date, sample_type, location, category, file="Manual entry", process_date="2022-09-04"):
  try:
    dbCurs.execute(sql.insert_sample, (sample_id, patient_id, receipt_date, sample_type, location, category, file, process_date))
  except Error as e:
    logging.error("db_methods.py:sampleInsertNew csv row {}: {}".format(row_number, e))

def samplesSelectByFile(file="Manual entry"):
  results = tryCatchSelect(sql.select_samples_by_original_file, (file,), "samplesSelectByFile")
  return results

def resultSelectRawBySampKey(sid):
  results = tryCatchSelect(sql.select_results_by_samp_key, (sid,), "resultSelectRawBySampKey")
  return results

def resultInsertNew(row_number, sample_id, analyte_id, analyte_value, file="Manual entry", process_date="2022-09-04"):
  try:                                  
    dbCurs.execute(sql.insert_result, (sample_id, analyte_id, analyte_value, file, process_date))
  except Error as e:
    logging.error("db_methods.py:resultInsertNew csv row {}: {}".format(row_number, e))

def analyteSelectByTest(test):
  results = tryCatchSelect(sql.select_analyte_by_code, (test,), "analyteSelectByTest")
  return results

if __name__ == '__main__':
  logging.info("Session started [dbmethods entry]")
  menu.db_main()
