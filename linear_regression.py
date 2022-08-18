import matplotlib.pyplot as plt
from scipy import stats
import db_methods
import datetime as dt
import hashlib

slope = 0
intercept = 0

def correlateX(x):
  return slope * x + intercept

def updatePatientLinearRegression(pid=0):
  s = []
  x = []
  y = []
  # Query the database by a known patient ID, then process results if the query doesn't return empty or false (from bad query)
  all_results = db_methods.selectSampleResultsByPatientID(pid)
  if all_results != False and all_results != []:
    # Loop through each row of the results to pull out the eGFR results of each blood sample
    # add the date and eGFR result to x and y axis lists, respectively
    # eGFR must be converted from str to float or the y axis won't be numeric/out of logical order
    for result in all_results:
      if result[3] == "Blood" and result[4] == "eGFR":
        s.append(result[1])
        x.append(dt.datetime.strptime(result[2],'%Y-%m-%d %H:%M').date().toordinal())
        y.append(float(result[6]))
    
    # Hash the list of samples to get a unique value, if found in the database, bypass doing the stats/update as there is no
    # change in previously used data
    h = hashlib.md5(str(s).encode('utf-8')).hexdigest()
    hash_results = db_methods.selectRegressionByPIDHash(pid, h)
    if hash_results == False or hash_results == [] or hash_results == None:
      global slope, intercept
      try:
        slope, intercept, r, p, std_err = stats.linregress(x, y)
      except:
        slope = 0 
        intercept = 0 
        r = 0 
        p = 0 
        std_err = 0
        print("Error with pid {}, values zeroed.".format(pid))
      d = dt.datetime.today().strftime("%Y-%m-%d %H:%M")
      n = len(x)
      db_methods.insertNewLinearRegression(pid, h, d, n, slope, intercept, r, p, std_err)
      db_methods.commitAndClose()

    else:
      print("Not updated, pid({}), no change in existing data hash({})".format(pid, h))
    
    #mymodel = list(map(correlateX, x))
    #print(mymodel)
    #plt.scatter(x, y)
    #plt.plot(x, mymodel)
    #plt.show()

def getPatientLinearRegression(pid=0):
  lr_results = db_methods.selectLatestRegressionByPID(pid)
  if lr_results != False and lr_results != []:
    print(lr_results)

def getAllLinearRegression():
  lr_results = db_methods.selectLatestRegressionByPID()
  if lr_results != False and lr_results != []:
    print("PID     |   MD5                              |   DateAdded        |  N     | slope                    | intersect             | r                       | p                      | std_err")
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    for r in lr_results:
      print(str(r[0]).rjust(6, " "), " | ", r[1], " | ", r[2], " | ", str(r[3]).rjust(4, " "), " | ", str(r[4]).rjust(22, " "), " | ", str(r[5]).rjust(19, " "), " | ", str(r[6]).rjust(21, " "), " | ", str(r[7]).rjust(22, " "), " | ")
  else:
    print("No results: ", lr_results)


if __name__ == '__main__':
  tick = 0
  print("LR started: ", dt.datetime.today().strftime("%Y-%m-%d %H:%M"))
  for id in range (40, 200):
    tick += 1
    updatePatientLinearRegression(id)
    if tick % 10 == 0:
      print(tick)
  print("LR stopped: ", dt.datetime.today().strftime("%Y-%m-%d %H:%M"))
  getAllLinearRegression()