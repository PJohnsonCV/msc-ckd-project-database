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
  print(data)
  if data != False:
    mdrd = []
    epi = [] 
    samps = []
    counter = 0
    print(data[1]['GFRE'])
    for cre in data[1]['CRE']:
      if cre != '':
        print(cre)
        egfr = calculateEGFR(patient, cre)
        mdrd.append(egfr[0])
        epi.append(egfr[1])
        samps.append(data[0][counter])
      counter += 1
    graph.generateSingleYChart(samps, (mdrd, epi))

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
  #ckdepi = min(Creat/SexK, 1)^SexA x max(Cre/SexK, 1)^-1.209 X 0.993^Age x Female (1.018) x Ethnicity (1.159)
  epiK = {'F': 0.7, 'M': 0.9 }
  epiA = {'F': -0.329, 'M': -0.411 }
  epiS = {'F': 1.018, 'M': 1 }
  ckd_epi = (min((creat/88.4) / epiK[patient['sex']],1) ** epiA[patient['sex']]) * (max((creat/88.4) / epiK[patient['sex']],1) ** -1.209) * (0.993 ** int(patient['age']))
  
  #mdrd = 175 X creat^-1.154 X age^-0.203 * Female (0.742) * Ethnicity (1.212)
  mdrdS = {'F': 0.742, 'M': 1}
  mdrd = 175 * (creat ** -1.154) * (patient['age'] ** -0.203) * mdrdS[patient['sex']]
  print(mdrd, ckd_epi)
  return (mdrd, ckd_epi)


if __name__ == '__main__':
    #mainMenu()
    compareEGFRCalculations()