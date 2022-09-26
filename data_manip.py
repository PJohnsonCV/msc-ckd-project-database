from datetime import date
import logging
import menus as menu
import db_methods as db
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(filename)s:%(funcName)s %(levelname)s\n                     %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

# Calculate the number of days between a sample receipt and the patient date of birth to produce an ordinal number relevant to the patient
# more relevant to personal care than ordinal date function that goes back to 0001.
def patientAgeOrdinal(dob, receipt, years=False):
  try:
    origin = date(int(dob[0:4]), int(dob[5:7]), int(dob[8:10]))
    current = date(int(receipt[0:4]), int(receipt[5:7]), int(receipt[8:10]))
    age = (current-origin).days +1
    if years==True:
      age = int(receipt[0:4]) - int(dob[0:4])
      if int(receipt[5:7])<int(dob[5:7]) or (int(receipt[5:7])==int(dob[5:7]) and int(receipt[8:10])<int(dob[8:10])):
        age-=1
    return age 
  except:
    logging.error("data_manip:patientAgeOrdinal bad format? dob {}, receipt {}, years {}".format(dob, receipt, years))
    return False
  
# MDRD equation using creatinine results in umol/L needs modifier to convert to mg/dL: divide by 88.4
# Excluding the ethnicity modifier because data isn't available from TelePath. 
# Calculation is: egfr = 175 x cre^-1.154 x age^-0.203 x Sex x Ethnicity
def calculateMDRD(sample_id, cre_result, sex, age):
  if(cre_result.strip() != "NA" and cre_result.isnumeric() and cre_result.strip() != "<5"):
    cre_result = int(cre_result)
  else:
    logging.error("Unable to calculate MDRD eGFR    for {}, creatinine '{}'".format(sample_id, cre_result))
    return False
  if sex == "F" or sex == "P": 
    sexx = 0.742
  elif sex == 'M':
    sexx = 1
  else:
    logging.error("Unable to calculate MDRD eGFR    for {}, patient sex '{}'".format(sample_id, sex))
    return False
  mdrd =  round(175 * (cre_result/88.4)**-1.154 * age**-0.203 * sexx)
  return mdrd

# CKD-EPI calculation using creatinine results in umol/L (UK standard), excluding the ethnicity modifier (data unavailable)
# Calculation is: egfr = 141 x min(Std Cre / K, 1)^a x max(Scre / K, 1)^-1.209 x 0.993^age x Sex x Ethnicity
# Rounding because telepath does, don't think there's clinical relevance to decimal values
def calculateCKDEPI(sample_id, cre_result, sex, age):
  #egfr = 141 x min(Std Cre / K, 1)^a x max(Scre / K, 1)^-1.209 x 0.993^age x F x Eth
  if(cre_result.strip() != "NA" and cre_result.isnumeric() and cre_result.strip() != "<5"):
    cre_result = int(cre_result)
  else:
    logging.error("Unable to calculate CKD-EPI eGFR for {}, creatinine '{}'".format(sample_id, cre_result))
    return False
  if sex == 'F' or sex =='P':
    Kval = 61.9
    alpha = -0.329
    sexx = 1.018
  elif sex == 'M':
    Kval = 79.6
    alpha = -0.411
    sexx = 1
  else:
    logging.error("Unable to calculate CKD-EPI eGFR for {}, patient sex '{}'".format(sample_id, sex))
    return False
  return round(141 * (min((cre_result / Kval),1)**alpha) * (max((cre_result / Kval), 1)**-1.209) * (0.993**age) * sexx)

# Already imported four years of data, not going to delete it all to rerun a csv import. Modifying tables with SQL and run this
# Adds ordinal dates being age in years, and age in days at point of sample receipt. Years is a formality, days will give useful regression 
def insertSampleAges():
  values = []
  samples = db.patientsampleSelectFromFilteredPIDs(2)
  logging.debug("insertSampleAges selected {} samples to update.".format(len(samples)))
  for sample in samples:
    days = patientAgeOrdinal(sample[0], sample[1])
    years = patientAgeOrdinal(sample[0], sample[1], True)
    values.append((days, years, sample[2]))
  logging.debug("insertSampleAges {} samples to update.".format(len(values)))
  db.updateSampleAges(values)

def insertCalculatedEGFR():
  values = []
  egfrM = db.analyteSelectByTest("MDRD")
  egfrC = db.analyteSelectByTest("CKDEPI")
  results = db.resultsGroupedByAnalyte('CRE', 2)
  logging.debug("insertCalculatedEGFR selected {} results to update.".format(len(results)))
  for result in results:
    if result[3].isnumeric():
      print(result[1], result[3], result[6], result[4])
      mdrd = calculateMDRD(result[1], result[3], result[6], result[4])
      epi = calculateCKDEPI(result[1], result[3], result[6], result[4])
      values.append((result[1], egfrM[0][0], mdrd, "Manual calculation", date.today()))
      values.append((result[1], egfrC[0][0], epi, "Manual calculation", date.today()))
  logging.debug("insertCalculatedEGFR {} results to insert.".format(len(values)))
  db.resultsInsertBatch(values)
  
if __name__ == '__main__':
  logging.info("Session started [data_manip entry]")
  menu.data_main()