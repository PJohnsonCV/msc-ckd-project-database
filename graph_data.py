import matplotlib.pyplot as plt
import numpy
import db_methods

# Data for plotting
x_time = ['samp1','samp2','samp3','samp4','samp5','samp6\n00/00/00']
s_data = [90,85,75,70,60,45]
s_data2 = [0.5,0.8,1.0,1.2,1.8,2.0]
s_data3 = [8, 16, 32, 64, 128, 256]

def dataGather(study_id, date_from, date_to):
  samp_list=[]
  result_dict={}
  
  samples = db_methods.selectPatientSamples(study_id, date_from, date_to)
  if samples != False:
    #Convert list to string for SQL use
    #sampleList = str(samples).replace('(', "").replace('),', "").replace("[","").replace(",)]","").replace("'","")
    for sample in samples:
      samp_list.append(sample[0])
      results = db_methods.selectSampleResults(sample[0])
      for result in results:
        if result[1] not in result_dict:
          result_dict[result[1]] = []
        result_dict[result[1]].append(float(result[2]))
    print(result_dict.keys())
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
  fig, axs = plt.subplots(6,2, figsize=(5,5), constrained_layout=True, squeeze = False)

  text_box = "X axis:\n"
  counter = 0
  for x in xlabels:
    counter+= 1
    text_box += "{} - {}\n".format(counter, x)

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
    'CRP': 300 
  }

  for x in range(3):
    for y in range(2):
      axs[x,y].set(xlabel='Sample', ylabel='eGFR (mL/min/1.73m$^{2}$)', xticks=range(len(xlabels)))
      axs[x,y].set_ylim([0,120])
  
      #Control lines to deliniate CKD stages approximated by eGFR ranges
      for control in stages:
        axs[x,y].plot(increments, numpy.full(len(increments), control['increments']), linewidth='1', color='tab:gray', alpha=0.5)
        axs[x,y].text(0.1, control['increments'], "Stage "+control['stage']+" ("+control['limit']+")", fontsize=6, color='tab:gray', alpha=0.75)
      #egfr
      axs[x,y].plot(increments, values['GFRE'], linewidth='2', color='tab:blue')
      axs[x,y].set_xticklabels(range(1,len(xlabels)+1)) #xlabels)
  
  #x = 0
  #y = 0
  #for key in values.keys():
  #  ax2 = axs[0,0].twinx()
  #  ax2.set_ylim(0, ylim[key])
  #  ax2.set(ylabel=key)
  #  ax2.plot(increments, values[key], linewidth='1', color='tab:red', label=key)
  #  y+= 1
  #  if y == 2:
  #    x += 1
  #    y = 0
  #  if x == 2:
  #    break  

  key = 'SOD'
  ax2 = axs[0,0].twinx()
  ax2.set_ylim(0,ylim[key]) 
  ax2.set(ylabel=key)
  ax2.plot(increments, values[key], linewidth='1', color='tab:red')

  key = 'POT'
  ax3 = axs[0,1].twinx()
  ax3.set_ylim(0,ylim[key]) 
  ax3.set(ylabel=key)
  ax3.plot(increments, values[key], linewidth='1', color='tab:red')

  key = 'CRE'
  ax4 = axs[1,0].twinx()
  ax4.set_ylim(0,ylim[key]) 
  ax4.set(ylabel=key)
  ax4.plot(increments, values[key], linewidth='1', color='tab:red')

  key = 'URE'
  ax5 = axs[1,1].twinx()
  ax5.set_ylim(0,ylim[key]) 
  ax5.set(ylabel=key)
  ax5.plot(increments, values[key], linewidth='1', color='tab:red')

  key = 'CRP'
  ax6 = axs[2,0].twinx()
  ax6.set_ylim(0,ylim[key]) 
  ax6.set(ylabel=key)
#  ax6.plot(increments, values[key], linewidth='1', color='tab:red')

  #key = ''
  #ax7 = axs[2,1].twinx()
  #ax7.set_ylim(0,400) 
  #ax7.set(ylabel=key)
  #ax7.plot(increments, values[key], linewidth='1', color='tab:red')

  plt.margins(x=0, y=0)
  #plt.tight_layout()
  fig.suptitle("\n".join([studyid]))
  #fig.text(1, 1, text_box, verticalalignment='top', horizontalalignment='right')
  fig.set_size_inches(10.5, 18.5)
  fig.savefig("test.png", dpi=96)

#generateChart(x_time, {'egfr':s_data, 'pho':s_data2, 'hb':s_data3})

dataGather(53, '1900-01-01', '2021-12-31')
plt.show()
#generateChart2(None, None)