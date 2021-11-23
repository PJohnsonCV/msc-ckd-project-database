import csv_parser
import db_methods
import graph_data as graph
import os

def doNothing():
    return True

def specificSearch():
    print("Specific Search")

def mainMenu():
  menu = ""  
  os.system('cls||clear')
  print("CKD Analysis\n------------\n")
  print("1. Process CSV")
  print("2. Specific Search")
  print("----------\n0. Exit")
  menu = input("Pick an option: ")
  fxDict.get(menu, lambda: 'Invalid')()
  if menu != 0:
    mainMenu()
    
fxDict = {
  '1': csv_parser.selectFile,
  '0': doNothing
}

def compareEGFRCalculations():
  patient = db_methods.selectOnePatientDetails(53)
  data = dataGather(53, '1900-01-01', '2021-12-31')
  print(patient)
  if data != False:
    mdrd = []
    epi09 = [] 
    epi21 = []
    samps = []
    counter = 0
    print(data[1]['GFRE'])
    for cre in data[1]['CRE']:
      if cre != '':
        egfr = calculateEGFR(patient, cre)
        mdrd.append(egfr[0])
        epi09.append(egfr[1])
        epi21.append(egfr[2])
        samps.append(data[0][counter])
      counter += 1
    graph.generateSingleYChart(samps, (mdrd, epi09, epi21), ("MDRD", "CKD-EPI 2009", "CKD-EPI 2021"))

def dataGather(study_id, date_from, date_to):
  samp_list=[]
  result_dict={'SOD': [],
    'POT': [],
    'URE': [],
    'CRE': [],
    'UMICR': [],
    'CRP': [],
    'PHO': [],
    'HBA1C': [],
    'HB': [],
    'HCT': [],
    'MCV': []}
  
  samples = db_methods.selectPatientSamples(study_id, date_from, date_to)
  if samples != False:
    for sample in samples:
      samp_list.append(sample[0])
      results = db_methods.selectSampleResults(sample[0])
      for result in results:
        if result[1] not in result_dict:
          result_dict[result[1]] = []
        result_dict[result[1]].append(float(result[2]))
      #make sure all lists are same size??
      longest_results = len(max(result_dict.values(), key=len))
      for x in result_dict:
        if len(result_dict[x]) < longest_results:
          result_dict[x].append(0)
    return (samp_list, result_dict)
  return False 

def calculateEGFR(patient, creat):
  creat = creat / 88.4 # umol/L to mg/dL
  cMod = 'g'
  if creat <= 0.7:
    cMod = 'l' 
  
  #ckdepi = min(Creat/SexK, 1)^SexA x max(Cre/SexK, 1)^-1.209 X 0.993^Age x Female (1.018) x Ethnicity (1.159)
  epiM = {'F': 144, 'M': 141}
  epiK = {'F09': 0.7, 'F21': 0.7, 'M09': 0.9, 'M21': 0.9 }
  epiA = {'F09l': -0.329, 'F09g': -1.209, 'F21l':-0.241, 'F21g': -1.2, 'M09l': -0.411, 'M09g': -1.209, 'M21l':-0.302, 'M21g': -1.2 }
  epiS = {'F': 1.018, 'M': 1, 'F21': 1.012, 'M21': 1}
  ckd_epi09 = epiM[patient['sex']] * ((creat/epiK[patient['sex']+'09'])**epiA[patient['sex']+'09'+cMod]) * (0.993 ** patient['age'])  
  ckd_epi21 = 142 * ((creat/epiK[patient['sex']+'21'])**epiA[patient['sex']+'21'+cMod]) * (0.9938 ** patient['age']) * epiS[patient['sex']+'21']

  #mdrd = 175 X creat^-1.154 X age^-0.203 * Female (0.742) * Ethnicity (1.212)
  mdrdS = {'F': 0.742, 'M': 1}
  mdrd = 175 * (creat ** -1.154) * (patient['age'] ** -0.203) * mdrdS[patient['sex']]
  print(mdrd, ckd_epi09, ckd_epi21)
  return (mdrd, ckd_epi09, ckd_epi21)


if __name__ == '__main__':
    #mainMenu()
    compareEGFRCalculations()