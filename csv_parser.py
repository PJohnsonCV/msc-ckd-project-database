# CSV Parser
# Data exported from laboratory information system will be in CSV format with a specific layout with one sample per row
# - column headers: Date Rec'd, Time Rec'd, Hospital No., Lab No/Spec No, Sex, DOB/Age, LOC, MSG, [tests]
# Process involves asking for file path/name, verifying file exists, process patient demographics, process sample details, process results
# Data MUST be processed in patient>sample>result order, as result is dependent on sample id, and sample is dependent on patient id
# Patient and sample details are straight forward, manipulation of dates to fix weird formatting issues, otherwise straight in (sample has patient age calculated from dob)
# Result processing includes some calculation of eGFR results as the gfr data in files could be MDRD or CKD-EPI depending on the date received, and this study is comparing the two calculations anyway
# Each processing loop builds an array of values to insert then performs an executemany - this is faster than inserting one at a time
from datetime import datetime
import os.path
import csv
import db_methods as db
import menus as menu
import data_manip as manip
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(filename)s:%(funcName)s %(levelname)s\n                     %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# Prompt the user for a file, or multiple files separated by comma
# Check the file exists then process it, skip if unsuccessfull
def selectFile(action=0):
  print("Please enter a path and filename, e.g. data/my_data.csv\nMultiple files can be processed sequentially. Use a comma to create a list, e.g. data/file1.csv, data/file2.csv\nType QUIT to go back to the menu.")
  file_path = input("File(s): ")
  if file_path.upper() == "QUIT":
    input("Action cancelled by user. Press ENTER to return to the menu.")
  else:
    if file_path.find(",") > -1:        #Process multiple
      files = file_path.split(",")
      logging.info("Multiple files provided: {}".format(files))
    else:
      files = [file_path]
      logging.info("Single file provided: {}".format(files))
    processFile(files, action)
    input("Any valid work has now concluded. Press ENTER to return to the menu.")
  menu.csv_main()

# File must exist and have a .csv extension. 
# Not the most robust, but enough for personal use
def fileValid(file_path):
  if os.path.isfile(file_path) and file_path.lower()[-4:] == ".csv":
    return True
  return False

# Requires a file path to perform a requested action on
# Default action=0, processess all data in the file (multiple pass)
# Specific actions = 1: just process patient IDs, 2: just process samples, 3: just process results, 4: samples and results
def processFile(file, action=0):
  count = 0
  start_time = datetime.now()
  if action == 0:
    logging.info("Action 0/All stages ----------------------------------------------------------------------------------")
    # Get all patient data before all sample data before all result data to ensure all dependencies are accomodated
    for f in file:
      count += 1
      f_time = debugTime("Step 1 of 3, PATIENTS from file {} of {}, {}".format(count, len(file), f))
      processPatientIDs(f.strip())
    logging.info("Stage 1/3 complete ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    count = 0
    for f in file:
      count += 1
      f_time = debugTime("Step 2 of 3, SAMPLES from file {} of {}, {}".format(count, len(file), f))
      processSamples(f.strip())
    logging.info("Stage 2/3 complete ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    count = 0
    for f in file:
      count += 1
      f_time = debugTime("Step 3 of 3, RESULTS from file {} of {}, {}".format(count, len(file), f))
      processResults(f.strip())
  elif action == 1:
    logging.info("Action 1/Patients only -------------------------------------------------------------------------------")
    for f in file:
      count += 1
      f_time = debugTime("Step 1 of 1, PATIENTS from file {} of {}, {}".format(count, len(file), f))
      processPatientIDs(f.strip())
  elif action == 2:
    logging.info("Action 2/Samples only --------------------------------------------------------------------------------")
    for f in file:
      count += 1
      f_time = debugTime("Step 1 of 1, SAMPLES from file {} of {}, {}".format(count, len(file), f))
      processSamples(f.strip())
  elif action == 3:
    logging.info("Action 3/Results only --------------------------------------------------------------------------------")
    for f in file:
      count += 1
      f_time = debugTime("Step 1 of 1, RESULTS from file {} of {}, {}".format(count, len(file), f))
      processResults(f.strip())
  #elif action == 4:
  #  start_time = debugTime("processFile [{}] 1/2 - samples   ".format(file))
  #  processSamples(file)
  #  step2_time = debugTime("processFile [{}] 2/2 - results   ".format(file))
  #  #print("Last step: {}".format(str(start_time - step2_time)))
  #  processResults(file)
  end_time = datetime.now()
  print("Time taken for all stages: {}".format(str(end_time - start_time)))
  logging.info("Time to complete action[{}] on {} file(s): {}".format(action, len(file), str(end_time - start_time)))

def singleSqlResult(sql_tuples):
  return sql_tuples[0]

# Complete, works with data 2016 - 2019 inclusive
def processPatientIDs(file):
  if fileValid(file):
    logging.info("[][][][][][][] PROCESSING FILE {} [][][][][][][]".format(file) )
    insert_values = [] 
    pid_list = set()
    tmp_list = set()
    proc_time = processTime()
    counters = {"row":0, "skip":0, "indb":0}
    
    ######## Ctrl Z here
    # Get a complete list of unique PIDs from the file before processing each line
    with open(file, 'r') as csv_file:
      csv_dict = csv.DictReader(csv_file)
      col_names = csv_dict.fieldnames
      for row in csv_dict:
        if row["Hospital No."].isnumeric():
          pid_list.add(row["Hospital No."])
   
    # Fetch a list of matching pids to reduce the number of tuples generated in later files
    str_join = ", ".join(pid_list)
    pt_query = db.patientSelectExistingIDsFromList(str_join)
    sql_result = set(map(singleSqlResult, pt_query))
        
    counters["row"] = 0
    #logging.debug("start of with open file 2")
    with open(file, 'r') as csv_file:
      csv_dict = csv.DictReader(csv_file)
      col_names = csv_dict.fieldnames
      for row in csv_dict:
        counters["row"]+=1 # Count all rows in file as the one thing I can easily compare in Notepad++/Excel 
        if row["Hospital No."].isnumeric() and int(row["Hospital No."]) not in sql_result and row["Hospital No."] not in tmp_list: # numeric, not in db, first encounter
          formatted_dob = formatDateTime(row["DOB/Age"], "00:00", False)
          if formatted_dob != False:
            tmp_list.add(row["Hospital No."])
            insert_values.append((int(row["Hospital No."]), formatted_dob, row["Sex"], "{} ({})".format(file,counters["row"]), proc_time))
            #Tuple translates to patient table: study_id, date_of_birth, sex, original_file, date_added
          else:   
            # Don't add the pid to pid_list in case a later instance of this pid has a correctly formatted dob
            logging.error("PATIENT EXCLUDED {}: formatted_dob is False on row {}".format(row["Hospital No."], counters["row"]))
        else: 
          counters["skip"]+=1 # Keeping count of pids encountered repetitively
          #logging.debug("counters[skip] incremented {}".format(counters["skip"]))
    #logging.debug("end of with open file")

    # Find an overlap of pids from the csv file, and those already stored in the patients table, then remove the duplicates from the list of values to insert
    # This was changed from line by line comparison in the with block, to a singular select in an attempt to reduce the processing time - I think the file processing
    # is the bottleneck, not the sql at this point. 
    if tmp_list != None and tmp_list != False and len(tmp_list) > 0:      
      #Finally, do the insert
      if len(insert_values) > 0:
        db.insertMany("patients", insert_values)
        if pt_query != None:
          counters["indb"] = len(pt_query)
        else:
          counters["indb"] = 0
        logging.info("-------------- COMPLETED FILE {} --------------\n                                - Rows in csv:            {}\n                                - Duplicated IDs in file: {}\n                                - IDs found in database:  {}\n                                - New IDs to add:         {}\n                                - Sum of the above:       {}".format(file, counters["row"], counters["skip"], counters["indb"], len(insert_values), int(counters["skip"]) + int(counters["indb"]) + len(insert_values)))
      else: 
        logging.info("len(insert_values) = 0; no further processing")
    else:
      logging.info("tmp_list = None or len(tmp_list) = 0; no further processing")
  else:
    logging.error("File not valid: {}".format(file))

# Potential to add patient check: get list of pids, compare to hospital no and reject sample if not in list of pids (no association)
def processSamples(file):
  if fileValid(file):
    logging.info("[][][][][][][] PROCESSING FILE {} [][][][][][][]".format(file))
    insert_values = []
    proc_time = processTime()
    counters = {"row":0, "success":0, "fail":0}
    with open(file, 'r') as csv_file:
      csv_dict = csv.DictReader(csv_file)
      col_names = csv_dict.fieldnames
      for row in csv_dict:
        counters["row"] += 1
        formatted_dob = formatDateTime(row["DOB/Age"], "00:00")
        if formatted_dob == False:
          formatted_dob = db.patientDOB(row["Hospital No."])
          logging.error("Bad date of birth in CSV {}, attempting to use value from database {}".format(row["DOB/Age"], formatted_dob))
        if formatted_dob != False:
          formatted_receipt = formatDateTime(row["Date Rec'd"], row["Time Rec'd"], True)
          if formatted_receipt != False:
            determined_type = bloodOrUrine(row['UMICR'])
            # Need to reject the sample if formatted_dob or formatted_receipt are wrong because the patient Age can't be calculated, and therefore useless data
            # However, need to track those samples as rejected, to add to discussion
            days = manip.patientAgeOrdinal(formatted_dob, formatted_receipt)
            years = manip.patientAgeOrdinal(formatted_dob, formatted_receipt, True)
            insert_values.append((row["Lab No/Spec No"], row["Hospital No."], formatted_receipt, days, years, determined_type, row["LOC"], row["MSG"], "{} ({})".format(file, counters["row"]), proc_time))
            #Tuple translates to sample table: samp_id_full, study_id, receipt_date, patient_age_days, patient_age_years, type, location, category, original_file, date_added
          else:
            logging.error("SAMPLE EXCLUDED {}: formatted_receipt is False on row {}".format(row["Lab No/Spec No"], counters["row"]))
        else:
          logging.error("SAMPLE EXCLUDED {}: formatted_dob is False on row {}".format(row["Lab No/Spec No"], counters["row"]))
      if len(insert_values) > 0:
        db.insertMany("samples",insert_values)
      else:
        logging.error("len(insert_values) = 0; no further processing")
    logging.info("-------------- COMPLETED FILE {} --------------\n                                - Rows in csv:       {}\n                                - New samples to add: {}".format(file, counters["row"], len(insert_values)))
  else:
    logging.error("File not valid: {}".format(file))

#
def processResults(file):
  if fileValid(file):
    logging.info("[][][][][][][] PROCESSING FILE {} [][][][][][][]".format(file))
    insert_values = []
    proc_time = processTime()
    counters = {"row":0, "success":0, "fail":0, "mdrd":0, "ckdepi":0}
    analytes = getAnalyteIDs(["Sodium","POT","Urea","CRE","eGFR","AKI","UMICR","CRP","IHBA1C","HbA1c","Hb","HCT","MCH","PHO","MDRD","CKDEPI"])
   
    with open(file, 'r') as csv_file:  
      csv_dict = csv.DictReader(csv_file)
      col_names = csv_dict.fieldnames
      #logging.debug("csv_parser:processResults [{}] Start FOR".format(file))
      for row in csv_dict:
        counters["row"] += 1

        for analyte in analytes:
          if analyte != "MDRD" and analyte != "CKDEPI" and row[analyte].strip() != "": 
            insert_values.append((row["Lab No/Spec No"], analytes[analyte], row[analyte], "{} ({})".format(file, counters["row"], ), proc_time))
            counters["success"] += 1
            if analyte == "CRE" and row[analyte].strip() != 'NA': # Non-blank creatinines can have eGFR calculated at this point
              formatted_dob = formatDateTime(row["DOB/Age"], "00:00")
              if formatted_dob == False:
                formatted_dob = db.patientDOB(row["Hospital No."])
                logging.error("Bad date of birth in CSV {}, attempting to use value from database {}".format(row["DOB/Age"], formatted_dob))
              
              formatted_receipt = formatDateTime(row["Date Rec'd"], row["Time Rec'd"], True)
              if formatted_dob != False and formatted_receipt != False:
                years = manip.patientAgeOrdinal(formatted_dob, formatted_receipt, True)
                if years != False and years > 0:
                  mdrd = manip.calculateMDRD(row["Lab No/Spec No"], row[analyte], row["Sex"], years)
                  if mdrd != False:
                    insert_values.append((row["Lab No/Spec No"], analytes["MDRD"], mdrd, "{} ({}) [Calculated at import]".format(file, counters["row"]), proc_time))
                    counters["success"] += 1
                    counters["mdrd"] += 1
                  ckdepi = manip.calculateCKDEPI(row["Lab No/Spec No"], row[analyte], row["Sex"], years)
                  if ckdepi != False:
                    insert_values.append((row["Lab No/Spec No"], analytes["CKDEPI"], ckdepi, "{} ({}) [Calculated at import]".format(file, counters["row"]), proc_time))
                    counters["success"] += 1
                    counters["ckdepi"] += 1
                else:
                  logging.info("Years is False or 0 on row {}, using dob {} and receipt {}".format(counters["row"], formatted_dob, formatted_receipt))
              else:
                logging.info("formatted_dob or formatted_receipt are False for sample on row {}: {}, {}".format(counters["row"], formatted_dob, formatted_receipt))
        #logging.debug("csv_parser:processResults end of analyte FOR")
    #logging.debug("processResults [{}] End FOR".format(file))
    if len(insert_values) > 0:
      db.insertMany("results", insert_values)
    logging.info("csv_parser:processResults, completed file={}\n                                rows in csv={}\n                                rows inserted={}\n                                mdrd={}\n                                ckdepi={}".format(file, counters["row"], counters["success"], counters["mdrd"], counters["ckdepi"]))
  else:
    logging.error("File not valid: {}".format(file))

# Assumes dict_time is correct: don't have a need to spend any time on validating this input right now
# This could be refactored, I'm sure of it, but I needed it spelled out line by line to make sure I didn't fudge any of the dates being handled
def formatDateTime(dict_date, dict_time, force20=False):
  date_str = dict_date.strip()
  y = 0
  m = 0
  d = 0
  if date_str != False:
    dotted = date_str.split(".") # 1900 unless < 32 (export year +10 margin), then 2000
    dashed = date_str.split("-") # Definitely 1900
    slashed = date_str.split("/") # Year is defined but might be wrong
    if len(dotted) == 3:
      y = "19" + str(dotted[2])
      if int(dotted[2]) < 10: # Oldest living person in UK, 2022 is 113y / b.1909 
        y = "20" + str(dotted[2])
      m = int(dotted[1])
      d = int(dotted[0])
    elif len(dashed) == 3: 
      y = "19" + str(dashed[2])
      m = int(dashed[1])
      d = int(dashed[0])
    elif len(dashed) == 2:
      logging.error("Dashed date has too few components: {}".format(dict_date))
      return False
    elif len(slashed) == 3:
      y = slashed[2]
      if int(slashed[2]) > 1999:
        y = int(slashed[2]) - 100
        # Not logging this manipulation because there's hundreds in each file
      m = int(slashed[1])
      d = int(slashed[0])
    else:
      logging.error("Unrecognisable date format: {}".format(dict_date))
      return False
    
    # If 100% certain the date is 2000+, force year to be 20XX
    if force20 == True:
      y = "20" + y[-2:]
    # Sense check month and days within normal ranges, though not to the extreme of d in 31, 30, 29, 28 depending on month etc.
    if m > 0 and m < 13:
      if d > 0 and d < 32:
        return "{}-{}-{} {}".format(y, str(m).rjust(2,"0"), str(d).rjust(2,"0"), dict_time)
      else:
        logging.error("Day must be <32, seen {}; {}".format(d, dict_date))
        return False  
    else:
      logging.error("Month must be <13, seen {}; {}".format(m, dict_date))
      return False

# If a sample has a urine albumin result, it must be a urine sample (UAlb is only urine test in LIMS export at this time)
def bloodOrUrine(umic_result):
  if umic_result.strip() != "":
    return 0  #urine
  return 1    #blood

# Create a dictionary of analyte IDs as stored in the db to test codes (from CSV files)
# Done this way to keep list of analytes flexible and accurate with database IDs
def getAnalyteIDs(tests):
  analytes = {}
  for test in tests:
    params = db.analyteSelectByTest(test)
    analytes[test] = params[0][0]
  return analytes

# Reused code to print the time at start and end of processes
# Returns the time in the event of wanting to find a delta or do something fancy
def debugTime(process_title):
  local_time = datetime.now()
  print("{}: {}".format(process_title, datetime.now()), flush=True)
  return local_time

# Helper function as dependent on other functions and changed from time.localtime to datetime.now in multiple locations in this file 
def processTime():
  dtn = datetime.now()
  return dtn.strftime("%Y-%m-%dT%H:%M:%S")

if __name__ == '__main__':
  logging.info("Session started [csvparser entry]")
  menu.csv_main()