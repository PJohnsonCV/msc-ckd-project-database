import matplotlib.pyplot as plt
from scipy import stats
import datetime as dt
import db_methods
import menus as menu
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(filename)s:%(funcName)s %(levelname)s\n                     %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

slope = 0
intercept = 0

def correlateX(x):
  print(slope * x + intercept)
  return intercept + slope * x

def prepareDataSet(patient_id, counter, set_name, sql_results):
  dataset = {"setname": set_name, "s": [], "x": [], "y": []}
  if sql_results != None:
    for result in sql_results:
      try:
        if result[2].isnumeric():
          dataset["s"].append(result[0])        #Samp_key
          dataset["x"].append(result[3])        #Patient age in days
          dataset["y"].append(float(result[2])) #Result as float
        else:
          logging.info("{} result excluded non-numeric: patient {}, sample {}, result {}".format(set_name, patient_id, result[0], result[3]))
        #return False #<- should this be commented out? wouldn't it exclude the who dataset?
      except:
        logging.error("Somehow this failed: {}, {} from {}".format(patient_id, result, sql_results))
      #  print("NoneType error spotted in prepareDataSet - check study.log")
  else:
    logging.info("{} results = None for {}, counter is {}".format(set_name, patient_id, counter))
    return False

  if len(dataset["s"])==0 and len(dataset["x"])==0 and len(dataset["y"])==0:
    logging.info("dataset is empty, {} patient sex is possibly not F M or P".format(patient_id))
    return False
  else:
    first_x = dataset["x"][0]
    xs = dataset["x"].count(first_x)
    if xs == len(dataset["x"]):
      logging.error("X-axis is replicates of {} for patient {}".format(first_x, patient_id))
      return False
  return dataset

def leastSquaresMDRDCKDEPI(patient_ids):
  logging.info("Linear Regression Data Gather -----------------------------------------------------------------------")
  if patient_ids == False or patient_ids == None:
    logging.error("No patient ids presented: {}".format(patient_ids))
    return False
  logging.info("{} patients will be processed".format(len(patient_ids)))

  counter = 0
  percent = round(0.20 * len(patient_ids))
  results = []
  
  for patient in patient_ids:
    patient=patient[0]
    counter += 1
    proc_time = dt.datetime.today().strftime("%Y-%m-%d %H:%M")
    
    if counter % percent == 0 or counter == len(patient_ids):
      pc = round(100 * (counter / len(patient_ids)))
      print("{} - {}%, {} of {} gathered".format(proc_time, pc, counter, len(patient_ids)), flush=True)

    if str(patient).isnumeric():
      resultsMDRD =   db_methods.resultsSingleAnalyteByPatient(int(patient), "MDRD")
      if resultsMDRD != False:
        mdrd = prepareDataSet(patient, counter, "MDRD", resultsMDRD)
        if mdrd != False:
          resultsCKDEPI = db_methods.resultsSingleAnalyteByPatient(int(patient), "CKDEPI") 
          if resultsCKDEPI != False:
            ckdepi = prepareDataSet(patient, counter, "CKD-EPI", resultsCKDEPI)
            if ckdepi != False:
              for dataset in [mdrd, ckdepi]:
                linreg = None
                try:
                  linreg = stats.linregress(dataset["x"], dataset["y"])
                  results.append((patient, dataset["setname"], ','.join(map(str, dataset["s"])), len(dataset["s"]), proc_time, str(linreg.slope), str(linreg.intercept), str(linreg.rvalue), str(linreg.pvalue), str(linreg.stderr), str(linreg.intercept_stderr)))
                except:
                  logging.error("Patient {} likely has replicated x-axis values: {}".format(patient, dataset))
            else:
              logging.error("MDRD data okay but CKD-EPI data unsuitible for linear regression for patient {}".format(patient))
          else:
            logging.error("No CKD-EPI results for patient {}".format(patient))
        else:
          logging.error("MDRD data unsuitible for linear regression for patient {}".format(patient))
      else:
        logging.error("No MDRD results for patient {}".format(patient))
    else:
      logging.error("Patient ID {} is not numeric, what happened?".format(patient))
  if len(results) > 0:
    db_methods.insertMany("linear_regression", results)
    logging.info("{} linear regression results committed".format(len(results)))
  else:
    logging.info("No linear regression results to commit.")
  logging.info("Linear regression data gather completed.")

# getPatientLinearRegression was NOT showing the regression line where the data sat, needed to show that regression on the fly matched the database values, and that output displayed as expected, left in as a useful troubleshooter
def regressSingleForTesting(pid=0):
  if pid.isnumeric() and int(pid) > 0: 
    resultsMDRD = db_methods.resultsSingleAnalyteByPatient(int(pid), "MDRD")
    mdrd = prepareDataSet(int(pid), 1, "MDRD", resultsMDRD)
    print(mdrd["y"])
    
    global slope, intercept
    linreg = stats.linregress(mdrd["x"], mdrd["y"])
    slope = linreg.slope
    intercept = linreg.intercept
    print(slope, intercept)

    mdrd_model = list(map(correlateX, mdrd["x"]))
    print(mdrd_model)

    plt.plot(mdrd["x"], mdrd["y"], 'o', label='original data')
    plt.plot(mdrd["x"], mdrd_model, 'r', label='MDRD regression')
    plt.legend()
    plt.show()


def quickMapX(list_values):
  return int(list_values[3])

def quickMapY(list_values):
  return int(list_values[2])

def patientAgeAndSampleID(list_values):
  return "{}\n{}".format(int(list_values[2]), list_values[5])

def getPatientLinearRegression(pid=0):
  if pid.isnumeric() and int(pid) > 0:
    resultseGFR = db_methods.resultsSingleAnalyteByPatient(int(pid), "eGFR")
    gfrX = list(map(quickMapX, resultseGFR)) # patient_age_days
    gfrY = list(map(quickMapY, resultseGFR)) # value

    regressionMDRD = db_methods.regressionSelectByPatientAndType(pid, "MDRD")
    resultsMDRD = db_methods.regressionSelectUsedResults(regressionMDRD[0][4], "MDRD")
    mdrd = prepareDataSet(int(pid), 1, "MDRD", resultsMDRD)
           
    global slope, intercept
    slope = regressionMDRD[0][7]
    intercept = regressionMDRD[0][8] 
    mdrd_model = list(map(correlateX, mdrd["x"]))
    mdrd_data = {"label": "MDRD regression", "values": mdrd_model}

    regressionCKDEPI = db_methods.regressionSelectByPatientAndType(pid, "CKD-EPI")
    resultsCKDEPI = db_methods.regressionSelectUsedResults(regressionCKDEPI[0][4], "CKDEPI") 
    ckdepi = prepareDataSet(int(pid), 1, "CKD-EPI", resultsCKDEPI)
    
    slope = regressionCKDEPI[0][7]
    intercept = regressionCKDEPI[0][8] 
    ckdepi_model = list(map(correlateX, ckdepi["x"]))
    ckdepi_data = {"label": "CKD-EPI regression", "values": ckdepi_model}

    models = [mdrd_data, ckdepi_data]

    xaxis_values = list(map(patientAgeAndSampleID, resultseGFR))
    displayChart(gfrX, gfrY, models, "Original TelePath eGFR", "Patient age (days)", "eGFR (mL/min/1.73m^2)") #, xaxis_values)
    
  elif pid == None:
    a=a
  else:
    logging.error("Likely a text ID provided when expecting a number or None")

# View separte from data as per webdev principles
def displayChart(x_data, y_data, regression_data, x_legend, x_label, y_label, x_tick=None):
  markers = ["r", "D", "^", "s", "p", "*", "d", "x"]
  
  plt.plot(x_data, y_data, 'o', label=x_legend)
  for regression in regression_data:
    i = regression_data.index(regression)
    plt.plot(x_data, regression["values"], markers[i], label=regression["label"])
  plt.xlabel(x_label)
  plt.ylabel(y_label)

  #  Want to highlight the renal disease stage based on eGFR result to add impact of regression
  plt.axhspan(0,15,0,1000000, facecolor='firebrick', alpha=0.5, zorder=-100) # Failure
  plt.axhspan(15.1,29.9,0,1000000, facecolor='lightcoral', alpha=0.5, zorder=-100) # 4
  plt.axhspan(30,44.9,0,1000000, facecolor='moccasin', alpha=0.5, zorder=-100) # 3b
  plt.axhspan(45,59.9,0,1000000, facecolor='palegoldenrod', alpha=0.5, zorder=-100) # 3a
  plt.axhspan(60,89.9,0,1000000, facecolor='palegreen', alpha=0.5, zorder=-100) # 2
  plt.axhspan(90,100,0,1000000, facecolor='limegreen', alpha=0.5, zorder=-100) # 1

  if x_tick != None:
    plt.xticks(x_data, x_tick, rotation='horizontal')
  
  plt.legend()
  plt.show()

if __name__ == '__main__':
  logging.info("Session started [linear_regression entry]")
  menu.db_main()