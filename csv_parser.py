import os.path
#from datetime import date
import time
import csv
import db_methods as db
import menus as menu
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(levelname)s | %(message)s', level=logging.DEBUG)

# Prompt the user for a file, or multiple files separated by comma
# Check the file exists then process it, skip if unsuccessfull
def selectFile(action=0):
  print("Enter a file path and file name (including extension). Multiple files can be listed using a comma. Type QUIT to exit.")
  file_path = input("File(s): ")
  if file_path.upper() == "QUIT":
    return False
  else:
    # Multiple files
    if file_path.find(",") > -1:
      for file in file_path.split(","):
        if fileValid(file):
          try:
            processFile(file, action)
          except:
            logging.error("selectFile did not complete try processFile({}, {}) ".format(file, action))
        else:
          logging.error("selectFile file did not pass validation ({})".format(file))
    # Single file
    else:
      if fileValid(file_path):
        processFile(file_path, action)
      else:
        logging.error("selectFile file did not pass validation ({})".format(file))
  input("Any valid work has now concluded. Press ENTER to continue.")
  menu.csv_main()

# File must exist and have a .csv extension. 
# Not the most robust, but enough for personal use
def fileValid(file_path):
  if os.path.isfile(file_path) and file_path.lower()[-4:] == ".csv":
    return True
  return False

# Requires a file path to perform a requested action on
# Default action=0, processess all data in the file in one go
# Specific actions = 1: just process patient IDs, 2: just process sample results
def processFile(file, action=0):
  if action == 0:
    start_time = debugTime("processFile full step 1/3 [{}]".format(file))
    processPatientIDs(file)
    mid_time = debugTime("processFile full step 2/3 [{}]".format(file))
    processSamplesSafetyOff(file)
    mid_time = debugTime("processFile full step 3/3 [{}]".format(file))
    processResultsSafetyOff(file)
    end_time = debugTime("processFile complete".format(file))
  elif action == 1:
    processPatientIDs(file)
  #elif action == 2:
    #processSample(file)

# Requires a file path to process. Validation handled outside of function,
# good enough for personal use, version 2 is a quick rewrite
# Create a list of IDs after inserting because the ID might appear in the file again, no point in second attempt at insert
def processPatientIDs(file):
  proc_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
  logging.info("processPatientIDS({}) proc_time={}\n-----------------------------------------------------------".format(file, proc_time))
  with open(file, 'r') as csv_file:
    csv_dict = csv.DictReader(csv_file)
    col_names = csv_dict.fieldnames
    pid_list = []
    row_counter = 0
    skip_counter = 0
    sql_counter = 0
    for row in csv_dict:
      row_counter+=1
      if row["Hospital No."] not in pid_list:
        pid_list.append(row["Hospital No."])
        formatted_dob = formatDateTime(row["DOB/Age"], "00:00")
        try:
          pt_query = db.patientSelectByID(row["Hospital No."])
          if pt_query == False or len(pt_query) == 0:
            db.patientInsertNew(row_counter, row["Hospital No."], formatted_dob, row["Sex"], file, proc_time)
          else:
            sql_counter+=1
        except:
          logging.error("processPatientIDs except row_counter [{}], Hospital No [{}], formatted_dob [{}], sex [{}], file [{}], proc_time [{}]".format(row_counter, row["Hospital No."], formatted_dob, row["Sex"], file, proc_time))
      else:
        skip_counter+=1
    db.commit()
    logging.info("processPatientIDs commit")
  logging.info("processPatientIDs COMPLETE for file [{}]\n          SUMMARY: row_counter [{}], pid_list+skip_counter [{}],  pid_list[{}], sql_counter[{}], skip_counter[{}]".format(file, row_counter, skip_counter+len(pid_list), len(pid_list), sql_counter, skip_counter))

# Just need the data in as fast as possible. Table has primary key on sample ID full and will reject duplicate entries, no need for existence check before insert
# Personal project, check previous commits for a more "appropriate" approach
def processSamplesSafetyOff(file):
  proc_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
  logging.info("processSamplesSafetyOff({}) BEGIN proc_time={}\n-------------------------------------------------------------------------------------------".format(file, proc_time))
  counters = {"row":0, "success":0, "fail":0}
  with open(file, 'r') as csv_file:
    csv_dict = csv.DictReader(csv_file)
    col_names = csv_dict.fieldnames
    logging.info("Start of FOR")
    for row in csv_dict:
      counters["row"] += 1
      try:
        formatted_receipt = formatDateTime(row["Date Rec'd"], row["Time Rec'd"])
        determined_type = bloodOrUrine(row['UMICR'])
        db.sampleInsertNew(counters["row"], row["Lab No/Spec No"], row["Hospital No."], formatted_receipt, determined_type, row["LOC"], row["MSG"], file, proc_time)
        counters["success"] += 1
      except:
        logging.error("failed row {}".format(counters["row"]))
        counters["fail"] += 1
    logging.info("End of FOR")
    db.commit()
  proc_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
  logging.info("processSamplesSafetyOff({}) END proc_time={}, rows in csv={}, rows inserted={}, rows not inserted={}\n-------------------------------------------------------------------------------------------".format(file, proc_time, counters["row"], counters["success"], counters["fail"]))

def processResultsSafetyOff(file):
  proc_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
  logging.info("processResultsSafetyOff({}) BEGIN proc_time={}\n-------------------------------------------------------------------------------------------".format(file, proc_time))    
  counters = {"row":0, "success":0, "fail":0}
  sample_ids = db.samplesSelectByFile(file)
  analytes = getAnalyteIDs(["Sodium","POT","Urea","CRE","eGFR","AKI","UMICR","CRP","IHBA1C","HbA1c","Hb","HCT","MCH","PHO"])

  with open(file, 'r') as csv_file:
    csv_dict = csv.DictReader(csv_file)
    col_names = csv_dict.fieldnames
    for row in csv_dict:
      counters["row"] += 1
      sample_info = [sid for sid in sample_ids if sid[1] == row["Lab No/Spec No"]]
      for analyte in analytes:
        if row[analyte].strip() != "": 
          try:
            db.resultInsertNew(counters["row"], sample_info[0][0], analytes[analyte], row[analyte], file, proc_time)
            counters["success"] += 1
          except:
            logging.error("failed row {}".format(counters["row"]))
            counters["fail"] += 1
    logging.info("End of FOR")
    db.commit()
  proc_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
  logging.info("processResultsSafetyOff({}) END proc_time={}, rows in csv={}, rows inserted={}, rows not inserted={}\n-------------------------------------------------------------------------------------------".format(file, proc_time, counters["row"], counters["success"], counters["fail"]))

#      # If the sample ID is found checking for and add the results
#      else:
#        sid = samp_query[0][0]
#        res_query = db.resultSelectRawBySampKey(sid)
#        #logging.debug("row {} | {} | {}".format(row_counter, sid, res_query))
#        if res_query == False or len(res_query) == 0:
#          res_counter += 1
#          for analyte in analytes:
#            if row[analyte].strip() != "":
#              res_counter += 1
#              db.resultInsertNew(row_counter, sid, analytes[analyte], row[analyte], file, proc_time)                      
#        else:
#          logging.info("csvparser.py - processSampleResult - sid ({}) not obtained from line {}".format(row["Lab No/Spec No"], row_counter))
#  db.commit()
#  logging.info("csvparser.py - processSampleResult Read {} rows - {} new samples, {} new sample results".format(row_counter, samp_counter, res_counter))

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
  local_time = time.localtime()
  print("{}: {}".format(process_title, time.asctime(local_time)), flush=True)
  logging.info("csvparser.py - {}: {}".format(process_title, time.asctime(local_time)))
  return local_time

if __name__ == '__main__':
  logging.info("Session started [csvparser entry]")
  menu.csv_main()