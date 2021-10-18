import matplotlib.pyplot as plt

# Data for plotting
x_time = ['01','02','03','04','05','06']
s_data = [90,85,75,70,60,45]
s_data2 = [0.5,0.8,1.0,1.2,1.8,2.0]
s_data3 = [8, 16, 32, 64, 128, 256]

def generate_chart(increments, values):
  fig, ax1 = plt.subplots()
  #ax.plot(increments, values['egfr'], 'b-', 
  #  increments, values['pho'], 'r-',
  #  increments, values['hb'], 'y-')

  ax1.set(xlabel='date', ylabel='eGFR', title='Study ID')
  ax1.plot(increments, values['egfr'], color='tab:blue')
  ax1.tick_params(axis='y', labelcolor='tab:blue')

  ax2 = ax1.twinx() 
  ax2.set(ylabel='pho')
  ax2.plot(increments, values['pho'], color='tab:red')
  
  ax3 = ax1.twinx()
  ax3.plot(increments, values['hb'], color = 'tab:green')

  fig.tight_layout()
  #ax.grid()
  fig.savefig("test.png")

generate_chart(x_time, {'egfr':s_data, 'pho':s_data2, 'hb':s_data3})
plt.show()