import matplotlib.pyplot as plt
from scipy import stats
import datetime as dt
import db_methods
import menus as menu
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(levelname)s | %(message)s', level=logging.DEBUG)

slope = 0
intercept = 0

def correlateX(x):
  return slope * x + intercept

def prepareDataSet(patient_id, counter, set_name, sql_results):
  dataset = {"setname": set_name, "s": [], "x": [], "y": []}
  if sql_results != None:
    for result in sql_results:
      try:
        if result[3].isnumeric():
          dataset["s"].append(result[0])        #Samp_key
          dataset["x"].append(result[4])        #Patient age in days
          dataset["y"].append(float(result[3])) #Result as float
        else:
          logging.info("{} result excluded non-numeric: patient {}, sample {}, result {}".format(set_name, patient_id, result[0], result[3]))
          return False
      except:
        logging.error("Somehow this failed: {}, {} from {}".format(patient_id, result, sql_results))
        print("NoneType error spotted in prepareDataSet - check study.log")
  else:
    logging.info("{} results = None for {}, counter is {}".format(set_name, patient_id, counter))
    return False
  return dataset

def regressCalculationComparison(patient_ids):
  logging.info("regressCalculationComparison started")
  counter = 0
  logging.info("{} patients pulled".format(len(patient_ids)))
  for patient in patient_ids:
    patient=patient[0]
    results = []
    counter += 1
    proc_time = dt.datetime.today().strftime("%Y-%m-%d %H:%M")
    
    if counter == round(0.01 * len(patient_ids)):
      pc = round(100 * (counter / len(patient_ids)))
      print("{} - {}%, {} of {} gathered".format(proc_time, pc, counter, len(patient_ids)), flush=True)

    logging.debug("Patient {} results gather:".format(patient))
    resultsMDRD = db_methods.resultsSingleAnalyteByPatient(int(patient), "MDRD")
    logging.debug("    MDRD fetched")
    resultsCKDEPI = db_methods.resultsSingleAnalyteByPatient(int(patient), "CKDEPI") 
    logging.debug("    CKD-EPI fetched")
    mdrd = prepareDataSet(patient, counter, "MDRD", resultsMDRD)
    logging.debug("    MDRD transformed")
    ckdepi = prepareDataSet(patient, counter, "CKD-EPI", resultsCKDEPI)
    logging.debug("    CKD-EPI transformed")
    
    for dataset in [mdrd, ckdepi]:
      if dataset != False:
        global slope, intercept
        try:
          logging.debug("    {} liniear regression started".format(dataset["setname"]))
          linreg = stats.linregress(dataset["x"], dataset["y"])
          logging.debug("    {} liniear regression ended".format(dataset["setname"]))
          results.append((patient, dataset["setname"], ','.join(str(dataset["s"])), len(dataset["s"]), proc_time, linreg.slope, linreg.intercept, linreg.rvalue, linreg.pvalue, linreg.stderr, linreg.intercept_stderr))
          logging.debug("    {} results appended".format(dataset["setname"]))
        except:
          logging.error("linregress error with {}".format(patient))
  logging.info("{} results to push to database".format(len(results)))
  db_methods.regressionInsertBatch(results)
  logging.info("regressCalculationComparison completed")
    
def getPatientLinearRegression(pid=0):
  s = []
  x = []
  y = []
  sample_results = all_results = db_methods.selectSampleResultsByPatientID(pid)
  regress_results = db_methods.selectLatestRegressionByPID(pid)
  if regress_results != False and regress_results != []:
    for result in sample_results:
      if result[3] == "Blood" and result[4] == "eGFR":
        s.append(result[1])
        x.append(dt.datetime.strptime(result[2],'%Y-%m-%d %H:%M').date().toordinal())
        y.append(float(result[6]))
    global slope, intercept
    slope = regress_results[0][4]
    intercept = regress_results[0][5]
    mymodel = list(map(correlateX, x))
    #print(mymodel)
    plt.scatter(x, y)
    plt.plot(x, mymodel)
    plt.show()
    print(regress_results)



if __name__ == '__main__':
  logging.info("Session started [linear_regression entry]")
  menu.db_main()