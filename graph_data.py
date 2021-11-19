import matplotlib.pyplot as plt
import numpy
import db_methods
from datetime import datetime

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
      #make sure all lists are same size
      longest_results = len(max(result_dict.values(), key=len))
      for x in result_dict:
        if len(result_dict[x]) < longest_results:
          result_dict[x].append(0)
    generateChart2x2(samp_list, result_dict, "{} \n {} - {}".format(study_id, date_from, date_to))
  return True 

def generateChart(xlabels, values):
  fig, ax1 = plt.subplots()

  increments = list(range(0, len(xlabels)))
  stages = [
    {'stage':'1', 'limit':'>90', 'increments':90},
    {'stage':'2', 'limit':'60-89', 'increments':60},
    {'stage':'3a', 'limit':'45-59', 'increments':45},
    {'stage':'3b', 'limit':'30-44', 'increments':30},
    {'stage':'4', 'limit':'15-29', 'increments':15},
    {'stage':'5', 'limit':'0-15', 'increments':0}
  ]

  ax1.set(xlabel='Sample ID / Date', ylabel='eGFR (mL/min/1.73m$^{2}$)', title='Study ID', xticks=range(len(xlabels)))
  ax1.set_ylim([0,120])
  
  #Control lines to deliniate CKD stages approximated by eGFR ranges
  for control in stages:
    ax1.plot(increments, numpy.full(len(increments), control['increments']), linewidth='1', color='tab:gray', alpha=0.5)
    ax1.text(0.1, control['increments'], "Stage "+control['stage']+" ("+control['limit']+")", fontsize=6, color='tab:gray', alpha=0.75)
  #egfr
  ax1.plot(increments, values['GFRE'], linewidth='2', color='tab:blue')
  print(values['SOD'])
  ax1.set_xticklabels(xlabels)
    
  ax2 = ax1.twinx()
  ax2.set_ylim(0,160) 
  ax2.set(ylabel='SOD')
  ax2.plot(increments, values['SOD'], linewidth='1', color='tab:red', label="Sodium")
  
  ax3 = ax1.twinx()
  ax3.set_ylim(0,8)
  ax3.set(ylabel='POT')
  ax3.plot(increments, values['POT'], linewidth='1', color='tab:green', label="Potassium")

 # ax3 = ax1.twinx()
 # ax3.plot(increments, values['POT'], color = 'tab:green')

  plt.margins(x=0, y=0, tight=True)
  plt.tight_layout()
  fig.savefig("test.png")

def generateChart2x2(xlabels, values, studyid):
  fig, axs = plt.subplots(6,2, figsize=(5, 5), constrained_layout=True, squeeze=False)

  increments = list(range(0, len(xlabels)))
  stages = [
    {'stage':'1', 'limit':'>90', 'increments':90},
    {'stage':'2', 'limit':'60-89', 'increments':60},
    {'stage':'3a', 'limit':'45-59', 'increments':45},
    {'stage':'3b', 'limit':'30-44', 'increments':30},
    {'stage':'4', 'limit':'15-29', 'increments':15},
    {'stage':'5', 'limit':'0-15', 'increments':0}
  ]
  ylim = {
    'SOD': 160,
    'POT': 8,
    'URE': 40,
    'CRE': 400,
    'UMICR': 20,
    'CRP': 300,
    'PHO': 2,
    'HBA1C': 120,
    'HB': 165,
    'HCT': 0.48,
    'MCV': 103
  }

  for x in range(6):
    for y in range(2):
      if x == 5 and y == 1:
        break
      axs[x,y].set(xlabel='Sample', ylabel='eGFR (mL/min/1.73m$^{2}$)', xticks=range(len(xlabels)))
      axs[x,y].set_ylim([0,120])
  
      #Control lines to deliniate CKD stages approximated by eGFR ranges
      for control in stages:
        axs[x,y].plot(increments, numpy.full(len(increments), control['increments']), linewidth='1', color='tab:gray', alpha=0.5)
        axs[x,y].text(0.1, control['increments'], "Stage "+control['stage']+" ("+control['limit']+")", fontsize=6, color='tab:gray', alpha=0.75)
      #egfr
      if 'GFRE' in values.keys():
        axs[x,y].plot(increments, values['GFRE'], linewidth='2', color='tab:blue')
      else:
        axs[x,y].plot(increments, values['GFR'], linewidth='2', color='tab:blue')
      axs[x,y].set_xticklabels(range(1,len(xlabels)+1), Fontsize=8) #xlabels)

  ax_list = [
    axs[0,0].twinx(),
    axs[0,1].twinx(),
    axs[1,0].twinx(),
    axs[1,1].twinx(),
    axs[2,0].twinx(),
    axs[2,1].twinx(),
    axs[3,0].twinx(),
    axs[3,1].twinx(),
    axs[4,0].twinx(),
    axs[4,1].twinx(),
    axs[5,0].twinx()
    #axs[5,1].twinx()
  ]
  
  ax=-1
  for key in ylim.keys():
    if key in values.keys():
      ax+=1
      ax_list[ax].set_ylim(0,ylim[key]) 
      ax_list[ax].set(ylabel=key)
      if len(values[key]) == len(increments):
        ax_list[ax].plot(increments, values[key], linewidth='1', color='tab:red')
  fig.delaxes(axs[5,1])

  plt.margins(x=0, y=0)
  fig.suptitle("Study_ID: {}\nPrinted: {}".format(studyid, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
  fig.set_size_inches(8.3, 11.7) #A4
  fig.savefig("test.png", dpi=96)
  #fig.savefig(datetime.now().strftime("%Y/%m/%d %H%M%S")+"_"+studyid, dpi=96)

#generateChart(x_time, {'egfr':s_data, 'pho':s_data2, 'hb':s_data3})

dataGather(53, '1900-01-01', '2021-12-31')
plt.show()
#generateChart2(None, None)