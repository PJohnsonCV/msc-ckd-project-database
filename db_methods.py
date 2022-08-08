import os
import sqlite3
from sqlite3 import Error
import db_menus
import db_statements as sql
#from time import localtime as ltime
from datetime import date

# Default settings for sqlite3 connection and cursor
dbname = "study_data.db" #"dbtest.db"
dbConn = sqlite3.connect(dbname)
dbCurs = dbConn.cursor()
#Uncomment to get juicy debug info on errors
#dbConn.set_trace_callback(print)

# Unordered list of all table names present in the database
tables = [
  'patient', 'sample', 'patient_sample', 'analyte', 'result', 'sample_result'
]

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

def commitAndClose():
  dbConn.commit()


# Print a list of tables and the number of rows each contains. 
# Purely for user information / curiosity
def displayTableRowCount():
  os.system('cls||clear')
  print("TABLE COUNTS\n-----------\n\n")
  for table in tables:
    count = selectTableCount(table)
    print("{}: {} rows".format(table, count))
  input()

# Pass in the required select from db_statements, and appropriate param values
# Not sure why I named this ONE, returns ALL rows from the select, or False if
# an execution error. 
# Minimises code reuse for all the selects used in the module. 
def tryCatchSelectOne(sql_string, values, method_name):
  try:
    dbCurs.execute(sql_string, values)
    rows = dbCurs.fetchall()
    return rows
  except Error as e:
    print("db_methods.py '{}' error: {}".format(method_name, e))
    #dbConn.close()
    return False

# Reusable select to get the number of rows in a table where the name is provided as a parameter
# Returns the value as a string (number or error message)
# Probably completely unsafe to do a string.format adding in a table name
# No type checking or other string sanitation - BAD! But couldn't think 
# of a way to do this without hardcoding multiple selects per table.
def selectTableCount(table_name):
  sql_string = "SELECT count(*) FROM {};".format(table_name)
  response = tryCatchSelectOne(sql_string, "", "selectTableCount")
  if response != False:
    response = response[0][0]
  return response

# Commits the CREATE TABLE script for all tables in one go
# Returns true on success or false on failure
# Only instance of executescript() in module, no need to refactor
def initialiseTables():
  try: 
    dbCurs.executescript(sql.define_tables)
    #dbConn.commit()
    print("Successfully created tables.")
    return True
  except Error as e:
    #dbConn.close()
    print("ERROR [db_methods.initialiseTables]: ", e)
    return False

# Populates the analytes table with the defined list, known_analytes
# Outputs the completion with the number of rows (assumed .rowcount
# is accurate), or the error code as necessary
def initialiseAnalytes():
  try:
    dbCurs.executemany(sql.insert_analytes, known_analytes)
    dbConn.commit() 
    print("Inserted {} of {} analyte(s)".format(dbCurs.rowcount, len(known_analytes)))
  except Error as e:
    #dbConn.close()
    print("ERROR [db_methods.initialiseAnalytes]: ", e)

def insertNewPatient(study_id, date_of_birth, sex=1, ethnicity=0):
  try:
    dbCurs.execute(sql.insert_patient, (study_id, date_of_birth, sex, ethnicity))
    #dbConn.commit() 
  except Error as e:
    #print("ERROR [db_methods.insertNewPatient]: ", e)
    return 0

def insertNewSample(sample_id, receipt_date, sample_type, patient_id):
  #print("In insertNewSample({}, {}, {}, {})".format(sample_id, receipt_date, sample_type, patient_id))
  try:
    dbCurs.execute(sql.insert_sample, (sample_id, receipt_date, sample_type)).lastrowid
    lastID = dbCurs.lastrowid
    #print("New sample, lastID: {}".format(lastID))
    dbCurs.execute(sql.insert_ptsamplink, (patient_id, sample_id))
    #dbConn.commit() 
    return lastID
  except Error as e:
    #print("ERROR [db_methods.insertNewSample]: ", e)
    return 0

def selectAnalyteParameters(a_code=None):
  try:
    dbCurs.execute("""SELECT id, code, descriptor, units FROM analyte WHERE code=?;""", [a_code])
    return dbCurs.fetchall()
  except Error as e:
    print("ERROR [db_methods.selectAnalyteParameters]: ", e)
    return None

def insertNewResult(samp_id, analyte_id, analyte_result):
  #print ("In insertNewResult({}, {}, {})".format(samp_id, analyte_id, analyte_result))
  try:
    dbCurs.execute(sql.insert_result, (analyte_id, analyte_result))
    result = dbCurs.lastrowid
    #print("insertNewResult -> ({}) {} = {}".format(result, analyte_id, analyte_result))
    dbCurs.execute(sql.insert_sampresultlink, (samp_id, result))
    #print("                -> ({}) {}".format(result, samp_id))
    #dbConn.commit()
    return result
  except Error as e:  
    print ("ERROR [db_methods.insertNewResult]: ", e)
    return 0
   
# Initialisation / reset of database
# Deletes tables if the exist, then creates them 
# Populates the analytes table with default values
# Outputs the row counts for each table to show success/failure
def resetDatabase():
  try:
    dbCurs.executescript(sql.bobby_tables)
    print("Tables deleted")
    if initialiseTables():
      initialiseAnalytes()
    displayTableRowCount()
    print("The following list of tables should be shown above: ")
    print(', '.join(str(item) for item in tables))
  except Error as e:
    print("Error deleting tables, ", e)



def selectSampleResults(samp_number):
  sql_string = """
    SELECT s.samp_id_full as 'SampleNo', 
           a.code as 'Analyte',
           r.value as 'Result',
           a.units as 'Units'
    FROM sample s
      JOIN sample_result sr ON (sr.samp_key = s.samp_key)
      JOIN result r ON (sr.result_id = r.id)
      JOIN analyte a ON (r.analyte_id = a.id)
    WHERE s.samp_id_full = ?;
  """
  results = tryCatchSelectOne(sql_string, (samp_number,), "selectSampleResults")
  return results

# Output patient data and count of samples associated with them
# Pass in integer patient_id
def printPatientDetails(patient_id):
  pt = selectOnePatientDetails(patient_id)
  if pt != False:
    age = "x"
    # Absolutely exploiting my lack of sanitation in selectTableCount 
    # addition of WHERE allows constraint of count to rows containing study_id
    sample_count = selectTableCount("patient_sample WHERE study_id={}".format(patient_id))
    print("ID: {} | DOB: {} (Age={}) | SEX: {} | ETHNICITY: {}".format(pt['id'],pt['dob'],age,pt['sex'],pt['ethnicity']))
    print("This patient has {} samples associated with their ID.\n".format(sample_count))
  else:
    print("The patient wasn't found (or an error occurred).\n")
  input("Press ENTER to continue.")

# Select row values from table: patient, for a given id
# Use with printPatientDetails to output 
def selectOnePatientDetails(patient_id):
  sql_string = "SELECT study_id, date_of_birth, sex, ethnicity FROM patient WHERE study_id = ?;"
  results = tryCatchSelectOne(sql_string, (patient_id,), "selectOnePatientDetails")
  if results != False and results != []:
    age = calculateAge(results[0][1])
    patient = {
      'id': results[0][0],
      'dob': results[0][1],
      'age': age, 
      'sex': results[0][2],
      'ethnicity': results[0][3]
    }
    return patient
  return False

def selectSampleResultsByID(sample_id):
  sql_string = """
    SELECT s.samp_key, s.samp_id_full, s.receipt_date, (CASE s.type WHEN 0 THEN 'Urine' WHEN 1 THEN 'Blood' END), a.code, a.descriptor, r.value, a.units 
    FROM sample s 
      JOIN sample_result sr ON (sr.samp_key = s.samp_key) 
      JOIN result r ON (sr.result_id = r.id)
      JOIN analyte a ON (r.analyte_id = a.id)
    WHERE s.samp_id_full LIKE ?;
  """
  results = tryCatchSelectOne(sql_string, ("%"+sample_id+"%",), "selectOneSampleResults")
  return results

def selectSampleResultsByPatientID(patient_id):
  sql_string = """
    SELECT s.samp_key, s.samp_id_full, s.receipt_date, (CASE s.type WHEN 0 THEN 'Urine' WHEN 1 THEN 'Blood' END), a.code, a.descriptor, r.value, a.units 
    FROM sample s 
      JOIN patient_sample ps ON (ps.samp_key = s.samp_id_full)
      JOIN sample_result sr ON (sr.samp_key = s.samp_key) 
      JOIN result r ON (sr.result_id = r.id)
      JOIN analyte a ON (r.analyte_id = a.id)
    WHERE ps.study_id = ?
    ORDER BY s.receipt_date ASC;
  """
  results = tryCatchSelectOne(sql_string, (patient_id,), "selectOneSampleResults")
  return results


def calculateAge(dobstr):
  dob = date(int(dobstr[:4]), int(dobstr[5:7]), int(dobstr[8:10]))
  today = date.today()
  age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
  return age

def printSampleResults(sample_id):
  current_id = ""
  serum_pivot = {} #{"", {"Sodium":"","POT":"","Urea":""}}
  results = selectSampleResultsByID(sample_id)
  if results != False and results != []:
    for result in results:
      print("{} | {} | {} | {} | {} ".format(result[1], result[3], result[4], result[6], result[7]))
      if result[1] not in serum_pivot:
        serum_pivot[result[1]] = {"Sodium":"", "POT":"", "Urea":"", "CRE":"", "eGFR":"", "AKI":"", "CRP":"", "IHBA1C":"", "HbA1c":"", "Hb":"", "HCT":"", "MCH":"", "PHO":""}
      serum_pivot[result[1]][result[4]] = result[6]
    print("Sample No.     | SOD | POT | UREA | CREA | eGFR | AKI | CRP | HbAC | IHbA | Hb  | HCT   | MCH | PHO ")
    for r in serum_pivot:  
      print("{} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {}".format(r, serum_pivot[r]['Sodium'].ljust(3," "), serum_pivot[r]['POT'].ljust(3, " "), serum_pivot[r]['Urea'].ljust(4, " "), serum_pivot[r]['CRE'].ljust(4, " "), serum_pivot[r]['eGFR'].ljust(4, " "), serum_pivot[r]['AKI'].ljust(3, " "), serum_pivot[r]['CRP'].ljust(3, " "), serum_pivot[r]['IHBA1C'].ljust(4, " "), serum_pivot[r]['HbA1c'].ljust(4, " "), serum_pivot[r]['Hb'].ljust(3, " "), serum_pivot[r]['HCT'].ljust(5, " "), serum_pivot[r]['MCH'].ljust(3, " "), serum_pivot[r]['PHO'].ljust(4, " ")))

  else:
    print("Sample ID not found.")
  input("\nPress ENTER to continue.")

def printPatientResults(pat_id):
  current_id = ""
  serum_pivot = {} #{"", {"Sodium":"","POT":"","Urea":""}}
  results = selectSampleResultsByPatientID(pat_id)
  if results != False and results != []:
    for result in results:
      if result[1] not in serum_pivot:
        serum_pivot[result[1]] = {"Sodium":"", "POT":"", "Urea":"", "CRE":"", "eGFR":"", "AKI":"", "CRP":"", "IHBA1C":"", "HbA1c":"", "Hb":"", "HCT":"", "MCH":"", "PHO":""}
      serum_pivot[result[1]][result[4]] = result[6]
    print("Sample No.     | SOD | POT | UREA | CREA | eGFR | AKI | CRP | HbAC | IHbA | Hb  | HCT   | MCH  | PHO ")
    for r in serum_pivot:  
      print("{} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {}".format(r, serum_pivot[r]['Sodium'].ljust(3," "), serum_pivot[r]['POT'].ljust(3, " "), serum_pivot[r]['Urea'].ljust(4, " "), serum_pivot[r]['CRE'].ljust(4, " "), serum_pivot[r]['eGFR'].ljust(4, " "), serum_pivot[r]['AKI'].ljust(3, " "), serum_pivot[r]['CRP'].ljust(3, " "), serum_pivot[r]['IHBA1C'].ljust(4, " "), serum_pivot[r]['HbA1c'].ljust(4, " "), serum_pivot[r]['Hb'].ljust(3, " "), serum_pivot[r]['HCT'].ljust(5, " "), serum_pivot[r]['MCH'].ljust(4, " "), serum_pivot[r]['PHO'].ljust(4, " ")))

  else:
    print("Patient ID not found.")
  input("\nPress ENTER to continue.")

# Output sample details for all samples associated to a patient_id (based on table patient_sample)
# Mode 0 Print a list of sample ids (default)
# Mode 1 Print a table of sample details 
# Mode 2 Print a table of sample details for samples in a range of dates 
def printPatientSamples(patient_id, mode=0, dfrom='1970-01-01', dto='2199-12-31'):
  if mode == 0 or mode == 1:
    results = selectPatientSamplesAll(patient_id)
  else:
    results = selectPatientSamplesDateRange(patient_id, dfrom, dto)

  if results != False and results != []:
    print("ID       | Sample Num.    | Received         | Type\n----------------------------------------------------")
    for sample in results:
      if mode == 0:
        print("           {}".format(sample[1]))
      else:
        stype = "S" if sample[3] == 1 else "U"
        print("{} | {} | {} | {}".format(str(sample[0]).ljust(8), sample[1], sample[2].ljust(16), stype)) #...
  input("\nPress ENTER to continue.")

# Select sample details for ALL samples associated to the patient id, no further constraint
# Use with printPatientSamples
def selectPatientSamplesAll(patient_id):
  sql_string = "SELECT s.samp_key, s.samp_id_full, s.receipt_date, s.type FROM sample s JOIN patient_sample ps ON (s.samp_id_full=ps.samp_key) WHERE ps.study_id=?;"
  results = tryCatchSelectOne(sql_string, (patient_id,), "selectPatientSamplesAll")
  if results != False and results != []:
    return results
  return False

# Select sample details for ALL samples associated to the patient id, between two dates (inclusive)
# Use with printPatientSamples
def selectPatientSamplesDateRange(patient_id, date_from, date_to):
  sql_string = "SELECT s.samp_key, s.samp_id_full, s.receipt_date, s.type FROM sample s JOIN patient_sample ps ON (s.samp_id_full=ps.samp_key) WHERE ps.study_id=? AND s.receipt_date >= ? AND s.receipt_date <= ?;"
  results = tryCatchSelectOne(sql_string, (patient_id, date_from, date_to,), "selectPatientSamplesDateRange")
  if results != False and results != []:
    return results
  return False

# Secondary entry point - should avoid running this as just a script. Compile the program
# and gain access to this module via menu.py (or db_menus.py) instead.
# Serious harm can come from playing about with the database in unstructured ways. KTHX
if __name__ == '__main__':
    db_menus.dbMenu()
