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
      slope, intercept, r, p, std_err = stats.linregress(x, y)
      d = dt.date.today().strftime("%Y-%m-%d %H:%M")
      db_methods.insertNewLinearRegression(pid, h, d, slope, intercept, r, p, std_err)
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

if __name__ == '__main__':
  #input = input("Enter a patient id:")
  #patientDataGather(input)
  for id in range (5, 100):
      updatePatientLinearRegression(id)

 