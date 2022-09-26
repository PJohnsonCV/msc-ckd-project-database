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
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(levelname)s | %(message)s', level=logging.INFO)

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
    step2_time = debugTime("processFile [{}] 2/3 - samples   ".format(file))
    #print("Last step: {}".format(str(step2_time - start_time)))
    processSamples(file)
    step3_time = debugTime("processFile [{}] 3/3 - results   ".format(file))
    #print("Last step: {}".format(str(step3_time - step2_time)))
    processResults(file)
  elif action == 1:
    if file.find(",") > -1:        #Process multiple
      for f in file.split(","):
        start_time = debugTime("processFile [{}] 1/1 - patientIDs".format(file))
        processPatientIDs(f)
    else:
      start_time = debugTime("processFile [{}] 1/1 - patientIDs".format(file))
      processPatientIDs(file)
  elif action == 2:
    start_time = debugTime("processFile [{}] 1/1 - samples   ".format(file))
    processSamples(file)
  elif action == 3:
    start_time = debugTime("processFile [{}] 1/1 - results   ".format(file))
    processResults(file)
  elif action == 4:
    start_time = debugTime("processFile [{}] 1/2 - samples   ".format(file))
    processSamples(file)
    step2_time = debugTime("processFile [{}] 2/2 - results   ".format(file))
    #print("Last step: {}".format(str(start_time - step2_time)))
    processResults(file)
  end_time = debugTime("processFile [{}] complete".format(file))
  print("Time taken: {}".format(str(end_time - start_time)))
  logging.info("csv_parser:processFile [{}] time to complete action[{}]: {}".format(file, action, str(end_time - start_time)))

def singleSqlResult(sql_tuples):
  return sql_tuples[0]

#
def processPatientIDs(file):
  if fileValid(file):
    logging.info("processPatientIDs processing file={} ----------------------".format(file) )
    insert_values = []
    pid_list = []
    proc_time = processTime()
    counters = {"row":0, "skip":0, "indb":0}
    with open(file, 'r') as csv_file:
      csv_dict = csv.DictReader(csv_file)
      col_names = csv_dict.fieldnames
      for row in csv_dict:
        counters["row"]+=1
        if row["Hospital No."] not in pid_list and row["Hospital No."].isnumeric(): # Not encountered this patient in this FILE yet
          formatted_dob = formatDateTime3(row["DOB/Age"], "00:00")
          if formatted_dob != False:
            pid_list.append(row["Hospital No."])
            insert_values.append((int(row["Hospital No."]), formatted_dob, row["Sex"], "{} ({})".format(file,counters["row"]), proc_time))
          else:          
            logging.error("Patient excluded {}: formatted_dob is False on row {}".format(row["Hospital No."], counters["row"]))
        else: # Patient has been encountered in the FILE already, so we are going to skip over it
          counters["skip"]+=1
    
    # create a string list for SQL statement
    if pid_list != None and len(pid_list) > 0:
      str_join = ", ".join(pid_list)


    if pid_list != None and len(pid_list) > 0:
      str_join = ", ".join(pid_list)
      pt_query = db.patientSelectExistingIDsFromList(str_join)
      sql_result = list(map(singleSqlResult, pt_query))
      if sql_result != None and len(sql_result) > 0:
        counters["indb"] = len(sql_result)
        
        if insert_values != None and len(insert_values) > 0:
          for study_id in sql_result:
            tup_out = [tup for tup in insert_values if tup[0] == study_id]
            insert_values.remove(tup_out[0])
          if insert_values != None and len(insert_values) > 0:
            logging.debug("insert_values length: {}".format(len(insert_values)))
          else:
            logging.debug("insert_values is empty after removal")
        else:
          logging.error("insert_values is empty before removal")
      else:
        logging.debug("pt_query length = 0, pt_query={}".format(pt_query))
      
      if len(insert_values) > 0:
        db.insertMany("patients", insert_values)
        if pt_query != None:
          counters["indb"] = len(pt_query)
        else:
          counters["indb"] = 0
        logging.info("csv_parser:processPatientIDs, completed file={}\n                                rows in csv:        {}\n                                duplicated in file: {}\n                                found in database:  {}\n                                patients to add:    {}".format(file, counters["row"], counters["skip"], counters["indb"], len(insert_values)))
      else: 
        logging.info("No values to insert ?is this an error")
    else:
      logging.info("No patients found in this file need processing ?is this an error")
  else:
    logging.error("processPatientIDs skipping invalid file {} ----------------------".format(file))

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
    db.insertMany("samples",insert_values)
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
          if analyte != "MDRD" and analyte != "CKDEPI" and row[analyte].strip() != "": 
            insert_values.append((sample_info, analytes[analyte], row[analyte], "{} ({})".format(file, counters["row"], ), proc_time))
            counters["success"] += 1
            if analyte == "CRE" and row[analyte].strip() != 'NA': # Non-blank creatinines can have eGFR calculated at this point
              formatted_dob = formatDateTime2(row["DOB/Age"], "00:00")
              formatted_receipt = formatDateTime2(row["Date Rec'd"], row["Time Rec'd"], True)
              if formatted_dob != False and formatted_receipt != False:
                years = manip.patientAgeOrdinal(formatted_dob, formatted_receipt, True)
                if years != False:
                  mdrd = manip.calculateMDRD(row["Lab No/Spec No"], row[analyte], row["Sex"], years)
                  if mdrd != False:
                    insert_values.append((sample_info, analytes["MDRD"], mdrd, "{} ({}) [Calculated at import]".format(file, counters["row"]), proc_time))
                    counters["success"] += 1
                    counters["mdrd"] += 1
                  ckdepi = manip.calculateCKDEPI(row["Lab No/Spec No"], row[analyte], row["Sex"], years)
                  if ckdepi != False:
                    insert_values.append((sample_info, analytes["CKDEPI"], ckdepi, "{} ({}) [Calculated at import]".format(file, counters["row"]), proc_time))
                    counters["success"] += 1
                    counters["ckdepi"] += 1
                else:
                  logging.info("csv_parser:processResults patientAgeOrdinal years is False on row {}".format(counters["row"]))
              else:
                logging.info("csv_parser:processResults formatted_dob or formatted_receipt are False for sample on row {}: {}, {}".format(counters["row"], formatted_dob, formatted_receipt))
        #logging.debug("csv_parser:processResults end of analyte FOR")
    logging.debug("processResults [{}] End FOR".format(file))
  if len(insert_values) > 0:
    db.insertMany("results", insert_values)
  logging.info("csv_parser:processResults, completed file={}\n                                rows in csv={}\n                                rows inserted={}\n                                mdrd={}\n                                ckdepi={}".format(file, counters["row"], counters["success"], counters["mdrd"], counters["ckdepi"]))

# TelePath outputs dates in dd.mm.yy or dd-mm-yy format depending on how close the year 
# is to being 100 years, i.e. an overlap "-21" = 1921 but ".21" = 2021 
# Convert to more sensible YYYY-MM-DD hh:mm format 
# UPDATE: Found a case of using slashes in real world data. 
def formatDateTime(dict_date, dict_time):
  try:
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
  except:
    logging.error("csv_parser:formatDateTime dict_date {}, dict_time {}".format(dict_date, dict_time))
  return fdate + " " + dict_time

def formatDateTime3(dict_date, dict_time):
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
      if int(dotted[2]) < 10: 
        y = "20" + str(dotted[2])
      m = int(dotted[1])
      d = int(dotted[0])
    elif len(dashed) == 3:
      y = "19" + str(dashed[2])
      m = int(dashed[1])
      d = int(dashed[0])
    elif len(dashed) == 2:
      logging.error("formatDateTime3 dashed date has too few components: {}".format(dict_date))
      return False
    elif len(slashed) == 3:
      y = slashed[2]
      if int(slashed[2]) > 1999:
        y = int(slashed[2]) - 100
        #logging.info("formatDateTime3 slashed date >1999 assumed to be 100 years incorrect and changed: {} now {}".format(dict_date, y))
      m = int(slashed[1])
      d = int(slashed[0])
    else:
      logging.error("formatDateTime3 unrecognisable date format: {}".format(dict_date))
      return False
    # Sense check month and days within normal ranges, though not to the extreme of d in 31, 30, 29, 28 depending on month etc.
    if m > 0 and m < 13:
      if d > 0 and d < 32:
        return "{}-{}-{} {}".format(y, str(m).rjust(2,"0"), str(d).rjust(2,"0"), dict_time)
      else:
        logging.error("formatDateTime3 day is an unacceptable value ({}), must be <32: {}".format(d, dict_date))
        return False  
    else:
      logging.error("formatDateTime3 month is an unacceptable value ({}), must be <13: {}".format(m, dict_date))
      return False


# Should probably be doing this with a regex, oh well
def formatDateTime2(date_str, time_str, rec=False):
  date_str = date_str.strip()
  date_out = "{}-{}-{}"
  if date_str != False:    
    slashed = date_str.split("/")
    if len(slashed) > 1:
      date_out = date_out.format("19" + slashed[2][-2:], slashed[1].rjust(2,"0"), slashed[0].rjust(2,"0"))
    else:
      dotted = date_str.split(".")
      if len(dotted) > 1:
        cent = "20"
        if int(dotted[2]) > 5 and rec==False: # 2022 - 17 (all 17 year old should be filtered out) = 2005
          cent = "19"
        date_out = date_out.format(cent + dotted[2], dotted[1], dotted[0])
      else:
        dashed = date_str.split("-")
        if len(dashed) > 1:
          date_out = date_out.format("19" + dashed[2], dashed[1], dashed[0])
        else:
          logging.error("csv_parser:formatDateTime2 date_str in unrecognised format")
          return False
    return "{} {}".format(date_out, time_str) 
  else:
    logging.error("csv_parser:formatDateTime2 date_str empty")
    return False

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