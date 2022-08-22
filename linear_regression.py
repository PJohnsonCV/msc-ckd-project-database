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
  if all_results != False and all_results != [] and len(all_results) > 1:
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
      #db_methods.commitAndClose()
    else:
      print("Not updated, pid({}), no change in existing data hash({})".format(pid, h))
  else: 
    print("{} not processed for conditional fail {} {} {}".format(pid, all_results!=False, all_results!=[], len(all_results)))
    
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
  min = 23000
  max = 28001
  print("LR started: ", dt.datetime.today().strftime("%Y-%m-%d %H:%M"))
  for id in range (min, max):
    tick += 1
    pc = round(100 * (tick / (max-min)))
    if pc % 10 == 0:
      print(pc, "% -", tick, dt.datetime.today().strftime("%Y-%m-%d %H:%M"), flush=True)
    updatePatientLinearRegression(id)
    if pc % 25 == 0:
      db_methods.commitAndClose()
  db_methods.commitAndClose()
  print("LR stopped: ", dt.datetime.today().strftime("%Y-%m-%d %H:%M"))
  
  #getAllLinearRegression()
  # started 19/8 20:35
  # ended        23:05
  # 998 patients  2:30
  # errors: 48 228 282 446 545

  # commit moved outside of loop
  # started 20/8 14:34
  # ended        15:39
  # 999 patients  1:05 -- 1997
  # errors: 1380, 1965

  # tick moved before update
  # started 20/8 
  # ended   
  # 3999 pts  -- 5996
  # errors: ALL FAIL NO COMMIT

  # added print \n and flush=True so can see update, added timestamp too
  # started 21/8 14:41
  # ended        15:41
  # 888 patients
  # errors: 2457 

  # added print @ 10%, commit @ 25%, min max 
  # started 21/8 16:55
  # ended        22:10
  # 5000 patients 5:15
  # errors:  3275 3455 4112 4482 4647 4779 4832 5620 5754 5885 6020 7400 7861 7934

  # 
  # started 21/8 22:34
  # ended   22/8 03:55
  # 5000 patients 5:21
  # errors:  9143 9818 10393 10709 10866 10945 12255 12260 

  # 
  # started 22/8   09:49
  # ended          20:38 
  # 10000 patients 10:49
  # errors:  13080 13414 13442 13616 14219 14526 15235 15248 15259 15453 16729 17702 17946 19044 19120 19659 20046 20321 20854 21394 22064 

  # 23000 patients so far,
  # 33 = 0 results, 1604 = 1 result == ~1hour processing time
  # 23000/282033 = 8.15% therefore could save about 12 hours processing time 
  # added and len(all_results) > 1 to first condition, and a print to give rejection criteria (for audit later)
  # started 22/8   23:00
  # ended           
  # 5000 patients 
  # errors:   
