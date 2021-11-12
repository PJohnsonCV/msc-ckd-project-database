import matplotlib.pyplot as plt
import numpy
import db_methods

# Data for plotting
x_time = ['samp1','samp2','samp3','samp4','samp5','samp6\n00/00/00']
s_data = [90,85,75,70,60,45]
s_data2 = [0.5,0.8,1.0,1.2,1.8,2.0]
s_data3 = [8, 16, 32, 64, 128, 256]

def dataGather():
  samp_list=[]
  result_dict={}
  
  samples = db_methods.selectPatientSamples(53, '1900-01-01', '2021-12-31')
  if samples != False:
    #Convert list to string for SQL use
    #sampleList = str(samples).replace('(', "").replace('),', "").replace("[","").replace(",)]","").replace("'","")
    for sample in samples:
      samp_list.append(sample[0])
      results = db_methods.selectSampleResults(sample[0])
      for result in results:
        if result[1] not in result_dict:
          result_dict[result[1]] = []
        result_dict[result[1]].append(result[2])
    
    #print(samp_list)
    print(result_dict['GFRE'])
    generateChart(samp_list, result_dict)
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
  
  ax1.tick_params(axis='y', labelcolor='tab:blue')
  ax1.set_xticklabels(xlabels)

 # ax2 = ax1.twinx() 
 # ax2.set(ylabel='SOD')
 # ax2.plot(increments, values['SOD'], color='tab:red')
  
 # ax3 = ax1.twinx()
 # ax3.plot(increments, values['POT'], color = 'tab:green')

  plt.margins(x=0, y=0, tight=True)
  plt.tight_layout()
  fig.savefig("test.png")

#generateChart(x_time, {'egfr':s_data, 'pho':s_data2, 'hb':s_data3})

dataGather()
plt.show()