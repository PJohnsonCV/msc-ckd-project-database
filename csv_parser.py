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
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(levelname)s | %(message)s', level=logging.DEBUG)

# Prompt the user for a file, or multiple files separated by comma
# Check the file exists then process it, skip if unsuccessfull
def selectFile(action=0):
  print("Please enter a path and filename, e.g. data/my_data.csv\nMultiple files can be processed sequentially. Use a comma to create a list, e.g. data/file1.csv, data/file2.csv\nType QUIT to go back to the menu.")
  file_path = input("File(s): ")
  if file_path.upper() == "QUIT":
    return False
  else:
    if file_path.find(",") > -1:        #Process multiple
      for file in file_path.split(","):
        tryProcess(file, action)
    else:
      tryProcess(file_path, action)     #Process single
  input("Any valid work has now concluded. Press ENTER to continue.")
  menu.csv_main()

# Tidier refactor :)
def tryProcess(file, action):
  file = file.strip() # In case of spaces between comma separation
  if fileValid(file):
    #try:
    processFile(file, action)
    #except:
    #  logging.error("selectFile did not complete try processFile({}, {}) ".format(file, action))
  else:
    logging.error("selectFile file did not pass validation ({})".format(file))

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
  logging.info("processFile action={}, file={}".format(action, file))
  if action == 0:
    logging.debug("csv_parser:processFile action 0")
    start_time = debugTime("processFile [{}] 1/3 - patientIDs".format(file))
    processPatientIDs(file)
    step2_time = debugTime("processFile [{}] 2/3 - samples".format(file))
    print("Last step: {}".format(str(step2_time - start_time)))
    processSamples(file)
    step3_time = debugTime("processFile [{}] 3/3 - results".format(file))
    print("Last step: {}".format(str(step3_time - step2_time)))
    processResults(file)
  elif action == 1:
    start_time = debugTime("processFile [{}] 1/1 - patientIDs".format(file))
    processPatientIDs(file)
  elif action == 2:
    start_time = debugTime("processFile [{}] 1/1 - samples".format(file))
    processSamples(file)
  elif action == 3:
    start_time = debugTime("processFile [{}] 1/1 - results".format(file))
    processResults(file)
  elif action == 4:
    start_time = debugTime("processFile [{}] 1/2 - samples".format(file))
    processSamples(file)
    step2_time = debugTime("processFile [{}] 2/2 - results".format(file))
    print("Last step: {}".format(str(start_time - step2_time)))
    processResults(file)
  end_time = debugTime("processFile [{}] complete".format(file))
  print("Time taken: {}".format(str(end_time - start_time)))
  logging.info("csv_parser:processFile [{}] time to complete action[{}]: {}".format(file, action, str(end_time - start_time)))

#
def processPatientIDs(file):
  logging.debug("csv_parser:processPatientIDs, started file={}".format(file))
  insert_values = []
  proc_time = processTime()
  counters = {"row":0, "skip":0, "indb":0}
  with open(file, 'r') as csv_file:
    csv_dict = csv.DictReader(csv_file)
    col_names = csv_dict.fieldnames
    pid_list = []
    for row in csv_dict:
      counters["row"]+=1
      if row["Hospital No."] not in pid_list and row["Hospital No."].isnumeric(): # Not encountered this patient in this FILE yet
        pid_list.append(row["Hospital No."])  # Now we have
        formatted_dob = formatDateTime(row["DOB/Age"], "00:00")
        pt_query = db.patientSelectByID(row["Hospital No."]) # Possibly don't need to do this, if solely relying on PRIMARY KEY constraint, could improve processing time
        if pt_query == False or len(pt_query) == 0: # Patient not found in DATABASE, therefore we need to insert it
          insert_values.append((int(row["Hospital No."]), formatted_dob, row["Sex"], "{} ({})".format(file,counters["row"]), proc_time))
        else: # Patient already found in DATABASE, so we don't want to insert again
          counters["indb"]+=1
      else: # Patient has been encountered in the FILE already, so we are going to skip over it
        counters["skip"]+=1
  if len(insert_values) > 0:
    db.patientInsertMany(insert_values)
  logging.info("csv_parser:processPatientIDs, completed file={}\n                                rows in csv:        {}\n                                duplicated in file: {}\n                                found in database:  {}\n                                patients to add:    {}".format(file, counters["row"], counters["skip"], counters["indb"], len(insert_values)))

#
def processSamples(file):
  logging.debug("csv_parser:processSamples, file={}".format(file))
  insert_values = []
  proc_time = processTime()
  counters = {"row":0, "success":0, "fail":0}
  with open(file, 'r') as csv_file:
    csv_dict = csv.DictReader(csv_file)
    col_names = csv_dict.fieldnames
    logging.debug("processSamples [{}] Start FOR".format(file))
    for row in csv_dict:
      counters["row"] += 1
      formatted_dob = formatDateTime(row["DOB/Age"], "00:00")
      formatted_receipt = formatDateTime(row["Date Rec'd"], row["Time Rec'd"])
      determined_type = bloodOrUrine(row['UMICR'])
      days = manip.patientAgeOrdinal(formatted_dob, formatted_receipt)
      years = manip.patientAgeOrdinal(formatted_dob, formatted_receipt, True)
      insert_values.append((row["Lab No/Spec No"], row["Hospital No."], formatted_receipt, days, years, determined_type, row["LOC"], row["MSG"], "{} ({})".format(file, counters["row"]), proc_time))
    logging.debug("processSamples [{}] End FOR".format(file))
  if len(insert_values) > 0:
    db.sampleInsertMany(insert_values)
  logging.info("csv_parser:processSamples, completed file={}\n                                rows in csv={}\n                                rows inserted={}".format(file, counters["row"], len(insert_values)))

#
def processResults(file):
  proc_time = processTime()
  logging.debug("csv_parser:processResults, file={}".format(file))
  counters = {"row":0, "success":0, "fail":0, "mdrd":0, "ckdepi":0}
  sample_ids = db.samplesSelectByFile("{}%".format(file))
  logging.debug("csv_parser:processResults {} sample_ids collected".format(len(sample_ids)))
  analytes = getAnalyteIDs(["Sodium","POT","Urea","CRE","eGFR","AKI","UMICR","CRP","IHBA1C","HbA1c","Hb","HCT","MCH","PHO","MDRD","CKDEPI"])
  logging.debug("csv_parser:processResults {} analytes".format(len(analytes)))
  insert_values = []
  with open(file, 'r') as csv_file:  
    csv_dict = csv.DictReader(csv_file)
    col_names = csv_dict.fieldnames
    logging.debug("csv_parser:processResults [{}] Start FOR".format(file))
    for row in csv_dict:
      counters["row"] += 1
      sample_info = [sid for sid in sample_ids if sid[1] == row["Lab No/Spec No"]]
      #logging.debug("csv_parser:processResults sample_info matched")
      if(len(sample_info) == 0):
        logging.error("No sample id on row {}".format(counters["row"]))
      else:
        sample_info = sample_info[0][0]
        for analyte in analytes:
          #logging.debug("csv_parser:processResults analyte FOR {}".format(analyte))
          if analyte != "MDRD" and analyte != "CKDEPI" and row[analyte].strip() != "": 
            insert_values.append((sample_info, analytes[analyte], row[analyte], "{} ({})".format(file, counters["row"], ), proc_time))
            #logging.debug("csv_parser:processResults insert_values for {}".format(analyte))
            counters["success"] += 1
            if analyte == "CRE" and row[analyte].strip() != 'NA': # Non-blank creatinines can have eGFR calculated at this point
              formatted_dob = formatDateTime(row["DOB/Age"], "00:00")
              formatted_receipt = formatDateTime(row["Date Rec'd"], row["Time Rec'd"])
              #logging.debug("csv_parser:processResults formatted dob and recepit date")
              years = manip.patientAgeOrdinal(formatted_dob, formatted_receipt, True)
              #logging.debug("csv_parser:processResults years got")
              mdrd = manip.calculateMDRD(row["Lab No/Spec No"], row[analyte], row["Sex"], years)
              #logging.debug("csv_parser:processResults mdrd got")
              if mdrd != False:
                insert_values.append((sample_info, analytes["MDRD"], mdrd, "{} ({}) [Calculated at import]".format(file, counters["row"]), proc_time))
                #logging.debug("csv_parser:processResults mdrd insert_values done")
                counters["success"] += 1
                counters["mdrd"] += 1
              ckdepi = manip.calculateCKDEPI(row["Lab No/Spec No"], row[analyte], row["Sex"], years)
              #logging.debug("csv_parser:processResults CKD EPI got")
              if ckdepi != False:
                insert_values.append((sample_info, analytes["CKDEPI"], mdrd, "{} ({}) [Calculated at import]".format(file, counters["row"]), proc_time))
                #logging.debug("csv_parser:processResults CKD EPI insert_values done")
                counters["success"] += 1
                counters["ckdepi"] += 1
        #logging.debug("csv_parser:processResults end of analyte FOR")
    logging.debug("processResults [{}] End FOR".format(file))
  if len(insert_values) > 0:
    db.resultsInsertBatch(insert_values)
  logging.info("csv_parser:processResults, completed file={}\n                                rows in csv={}\n                                rows inserted={}\n                                mdrd={}\n                                ckdepi={}".format(file, counters["row"], counters["success"], counters["mdrd"], counters["ckdepi"]))

# TelePath outputs dates in dd.mm.yy or dd-mm-yy format depending on how close the year 
# is to being 100 years, i.e. an overlap "-21" = 1921 but ".21" = 2021 
# Convert to more sensible YYYY-MM-DD hh:mm format 
# UPDATE: Found a case of using slashes in real world data. 
def formatDateTime(dict_date, dict_time):
  slash = dict_date.split("/")
  if len(slash) > 1:
    #if(int(slash[2]) > 2016): # Commented out as there shouldn't be any patients <17yo
    slash[2] = "19" + slash[2][-2:]
    fdate = slash[2] + "-" + slash[1].rjust(2,"0") + "-" + slash[0].rjust(2,"0")
  else: 
    prefix = "20"
    if dict_date[-3] == "-" or int(dict_date[-2:]) > 22: #TP autoformats close-to dobs 
      prefix = "19"
    fdate = prefix + dict_date[-2:] + "-" + dict_date[3:5] + "-" + dict_date[:2]
  return fdate + " " + dict_time

# If a sample has a urine albumin result, it must be a urine sample
def bloodOrUrine(umic_result):
  if umic_result.strip() != "":
    return 0  #urine
  return 1    #blood

# Create a dictionary of analyte IDs as stored in the db to test codes (from CSV files)
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