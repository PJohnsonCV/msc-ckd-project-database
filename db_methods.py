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
  ("PHO", "Phosphate", "mmol/L"),
  ("MDRD", "eGFR by MDRD self calc", "mL/min/1.73m^2"),
  ("CKDEPI", "eGFR by CKD-EPI self calc", "mL/min/1.73m^2")
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
  insertMany("analytes", known_analytes)

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
    logging.error("db_methods.py:resetDatabase {}".format(e))

def alterDatabase():
  if(sql.alter_tables != ""):
    print("Found the following SQL string:\n{}".format(sql.alter_tables))
    confirm = input("If you want to execute the SQL statement(s) above, type YES: ")
    if confirm.upper() == "YES":
      try:
        dbCurs.executescript(sql.alter_tables)
        logging.info("db_methods.py:alterDatabase - the following SQL was executed: {}".format(sql.alter_tables))
        input("Tables altered. Press ENTER to continue.")
      except Error as e:
        logging.error("db_methods.py:alterDatabase {}".format(e))
    else:
      input("Response not as expected, backing out of alter. Press ENTER to continue.")
  else:
    input("No valid SQL string found. Press ENTER to continue.")
    logging.info("db_methods.py:alterDatabase no SQL string found to execute")

def updateSampleAges(values):
  try:
    dbCurs.executemany(sql.update_samples_ordinal_ages, values)
    commit() 
    logging.info("db_methods.py:updateSampleAges Updated {} of {} samples(s)".format(dbCurs.rowcount, len(known_analytes)))
  except Error as e:
    logging.error("dbmethods.py:updateSampleAges {}".format(e))

# Pass in the required select from db_statements, and appropriate param values
# Not sure why I named this ONE, returns ALL rows from the select, or False if
# an execution error. 
# Minimises code reuse for all the selects used in the module. 
def tryCatchSelect(sql_string, values, method_name):
  #dbConn.set_trace_callback(print)
  try:
    if values != None:
      dbCurs.execute(sql_string, values)
    else:
      dbCurs.execute(sql_string)
    rows = dbCurs.fetchall()
    return rows
  except Error as e:
    logging.debug("tryCatchSelect sql_string [{}], values [{}], method_name [{}]".format(sql_string, values, method_name))
    logging.error("tryCatchSelect:{}, error: {}".format(method_name, e))
    return False
  

# Helper functions help keep things tidy!
def commit():
  dbConn.commit()
  logging.info("Database committed")

def patientSelectByID(pid):
  results = tryCatchSelect(sql.select_patient_by_id, (pid,), "patientSelectByID")
  return results

def patientSelectExistingIDsFromList(pids):
  s = sql.matching_patient_ids_in_given_list.format(pids)
  results = tryCatchSelect(s, None, "patientSelectExistingIDsFromList")
  return results

# Groups study_id having a count greater than n in the sample table, excludes <= n obviously, so good to prevent processing 0 / 1 / 2 samples for linear regression
def patientsSelectSampleCountGreaterThan(count_gt,sample_type=2):
  sql_str = sql.select_patient_id_if_multiple_samples
  if sample_type == 0:
    sql_str = sql.select_patient_id_if_multiple_samples_urine
  elif sample_type == 1:
    sql_str = sql.select_patient_id_if_multiple_samples_serum
  results = tryCatchSelect(sql_str, (count_gt,), "patientsSelectSampleCountGreaterThan")
  return results

def patientsampleSelectFromFilteredPIDs(count_gt):
  results = tryCatchSelect(sql.select_patientsample_using_pids, (count_gt,), "patientssampleSelectFromFilteredPIDs")
  return results

def patientInsertSingle(row_number, study_id, date_of_birth, sex=1, file="Manual entry", process_date="2022-09-04"):
  try:
    dbCurs.execute(sql.insert_patient, (study_id, date_of_birth, sex, file, process_date))
  except Error as e:
    logging.error("db_methods.py:patientInsertSingle csv row {}: {}".format(row_number, e))

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

def resultsGroupedByAnalyte(code, count_gt):
  results = tryCatchSelect(sql.select_grouped_results_by_analyte, (code, count_gt,), "samplesSelectByFile")
  return results

def resultSelectRawBySampKey(sid):
  results = tryCatchSelect(sql.select_results_by_samp_key, (sid,), "resultSelectRawBySampKey")
  return results

def resultsSingleAnalyteByPatient(pid, analyte):
  results = tryCatchSelect(sql.select_results_by_analyte_patient, (pid, analyte,), "resultsSingleAnalyteByPatient")
  return results

def resultInsertNew(row_number, sample_id, analyte_id, analyte_value, file="Manual entry", process_date="2022-09-04"):
  try:                                  
    dbCurs.execute(sql.insert_result, (sample_id, analyte_id, analyte_value, file, process_date))
  except Error as e:
    logging.error("db_methods.py:resultInsertNew csv row {}: {}".format(row_number, e))

def analyteSelectByTest(test):
  results = tryCatchSelect(sql.select_analyte_by_code, (test,), "analyteSelectByTest")
  return results

def regressionSelectByPatientAndType(pid=0, type=None):
  if pid == 0 and type == 0:
    results = None
  elif pid != 0 and type == None:
    str = sql.select_regression_by_pid
    results = tryCatchSelect(str, (pid,), "regressionSelectByPatientAndType pid only")
  elif pid == 0 and type != None:
    str = sql.select_regression_all_by_type
    results = tryCatchSelect(str, (type, ), "regressionSelectByPatientAndType type only")
  elif pid != 0 and type != None:
    str = sql.select_regression_by_pid_and_type
    results = tryCatchSelect(str, (pid, type, ), "regressionSelectByPatientAndType pid + type")
  return results

def regressionSelectUsedResults(samp_ids, analyte_code):
  formatted = sql.select_regression_results_used.format(samp_ids)
  results= tryCatchSelect(formatted, (analyte_code,), "regressionSelectUsedCREResults")
  return results

# Single definition to keep the module organised -> removes the same code for specific debug strings 
def insertMany(to_table, values):
  table_definitions = {
    "patients" : ("patient", sql.insert_patient, 5), 
    "samples"  : ("sample",  sql.insert_sample, 10), 
    "results"  : ("result",  sql.insert_result, 5), 
    "analytes" : ("analyte", sql.insert_analytes, 3), 
    "linear_regression" : ("linear_regression", sql.insert_linearregression, 11)
  }
  if to_table in table_definitions:
    #logging.debug("db_methods:insertMany {} records, {} provided parameters, {} expected parameters".format(len(values), len(values[0]), table_definitions[to_table][2]))
    if len(values) > 0 and len(values[0]) == table_definitions[to_table][2]:
      try:
        dbCurs.executemany(table_definitions[to_table][1], values)
        commit()
        logging.info("db_methods:insertMany {} successfully committed {} values".format(to_table, len(values)))
      except Error as e:
        logging.error("db_methods:insertMany failed to insert values to '{}', size of tuple: {}. Error thrown: {}".format(to_table, len(values), e))
        logging.debug("tuple contents:\n{}".format(values))
    else:
      logging.error("db_methods:insertMany 'values' has an incorrect number of values for '{}'; expecting {}, counted {}".format(to_table, table_definitions[to_table], len(values)))
      return False
  else:
    logging.error("db_methods:insertMany 'to_table' is not in list of table_definitions '{}'".format(to_table))
    return False

def tableCounts():
  sql_str = []
  for table in sql.list_tables:
    sql_str.append("SELECT count(*), '{}' as '{}' FROM {} ".format(table, table, table))
  union = 'UNION '.join(sql_str) + " ORDER BY 2;"
  results = tryCatchSelect(union, None, "tableCounts")
  return results

if __name__ == '__main__':
  logging.info("Session started [dbmethods entry]")
  menu.db_main()
