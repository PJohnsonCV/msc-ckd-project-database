import csv_parser as csv
import db_methods as db
import data_manip as customs
import linear_regression as linreg
import os
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(filename)s:%(funcName)s %(levelname)s\n                     %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

def csv_main():
  os.system('cls||clear')
  print("CSV Parser\n----------\n")
  print("1. Everything")
  print("2. Patients only")
  print("3. Samples only")
  print("4. Results only")
  #print("5. Import samples and results (not patients)")
  print("ENTER to go back to the main menu")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    csv.selectFile(0)
  elif selection == "2":
    csv.selectFile(1)
  elif selection == "3":
    csv.selectFile(2)
  elif selection == "4":
    csv.selectFile(3)
  else:
    program_main()

def db_main():
  os.system('cls||clear')
  print("Database Control\n----------------\n")
  print("1. View table record counts")
  print("9. [ADVANCED] Database Maintenance")
  print("ENTER to go back to the main menu")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    dbRecordCounts()
  elif selection == "9":
    dbDangerMenu()
  else:
    program_main()

def dbRecordCounts():
  results = db.tableCounts()
  os.system('cls||clear')
  print("Database Control > Table Record Counts\n--------------------------------------\n")
  print("Table             | Records\n-----------------------------")
  for result in results:
    print("{} | {}".format(result[1].ljust(17,' '), result[0]))
  selection = input("\nENTER to go back to the Database Control menu\n")
  db_main()

def dbDangerMenu():
  os.system('cls||clear')
  print("Database Control - DANGER ZONE !!!\n----------------------------------\n")
  print("A. Alter Tables\n   This relies on db_strings.alter_tables having SQL string(s) present.")
  print("F. Any custom fixes to run after reset/alter.\n   This should be called after running Alter Tables, and is dependent on menus.dbDangerMenu having function calls.")
  print("R. Reset/Initialise\n   This deletes the tables and all data within, then recreates with only the analyte data present. !!! BACK UP THE DATABASE FILE FIRST !!!")
  print("ENTER to go back to the database control menu")
  selection = input("\nEnter your choice: ")
  if selection.upper() == "A":
    db.alterDatabase()
  elif selection.upper() == "F":
    # Add appropriate function calls here
    print("Nothig to run")
  elif selection.upper() == "R":
    dbResetPanic()
  else:
    db_main()

def dbResetPanic():
  os.system('cls||clear')
  print("Database Control: RESET DATABASE\n--------------------------------\n\n")
  print("! ----------------------- !!! WARNING !!! ----------------------- !\n")
  print("! Resetting the database will result in TOTAL DATA LOSS.          !\n")
  print("! Do NOT reset without due cause, and backup any necessary data.  !\n")
  print("! ----------------------- !!! WARNING !!! ----------------------- !\n\n")
  selection = input("Type 'QUIT' to go back to the menu, or 'CONT' to continue with a database reset: ")
  if selection.upper() == "QUIT":
    db_main()
  elif selection.upper() == "CONT":
    print("\nTo confirm you want to reset the database, type the following message: \n")
    confirm = input("I WANT TO RESET THE DATABASE\n")
    if confirm.upper() == "I WANT TO RESET THE DATABASE":
      dblconfirm = input("\nAre you sure? Y/N: ")
      if dblconfirm.upper() == "Y":
        db.resetDatabase()
        input("\nYou have reset the database. Press ENTER to continue.")
    #input("\nDatabase was NOT reset because you cancelled or didn't pass a check. Press return to go back to the menu.\n")
  db_main()

def data_main():
  os.system('cls||clear')
  print("Data modification etcetra\n-------------------------\n")
  print("1. Random IDs from 2020")
  #print("1. Add ordinal age to samples")
  #print("2. Add MDRD and CKD-EPI calculations to results")
  print("ENTER to go back to the main menu")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    randomIDs()
  program_main()

def randomIDs():
  os.system('cls||clear')
  print("Output lists of random study_ids\n--------------------------------\n")
  print("1. No change")
  print("2. Downward")
  print("3. Upward")
  print("4. Contains cat 4 / 5 definitely")
  print("ENTER to go back to the main menu")
  selection = input("\nEnter your choice: ")
  q = "How many {} do you want?"
  if selection == "1":
    selection = input(q.format("NO CHANGE"))
    #if selection.isnumeric():
    print("Here's a list of random IDs:")
    ids = customs.getRandomIDs(1, selection)
    print(ids)
    print("----------------------------")
  elif selection == "2":
    selection = input(q.format("DOWNWARD CHANGE"))
    #if selection.isnumeric():
    print("Here's a list of random IDs:")
    ids = customs.getRandomIDs(2, selection)
    print(ids)
    print("----------------------------")
  elif selection == "3":
    selection = input(q.format("UPWARD CHANGE"))
    #if selection.isnumeric():
    print("Here's a list of random IDs:")
    ids = customs.getRandomIDs(3, selection)
    print(ids)
    print("----------------------------")
  elif selection == "4":
    selection = input(q.format("UPWARD CHANGE WITH 4 / 5 ONLY"))
    #if selection.isnumeric():
    print("Here's a list of random IDs:")
    ids = customs.getRandomIDs(4, selection)
    print(ids)
    print("----------------------------")
  elif selection == "5":
    selection = input(q.format("100% RANDOM"))
    #if selection.isnumeric():
    print("Here's a list of random IDs:")
    ids = customs.getRandomIDs(0, selection)
    print(ids)
    print("----------------------------")
  data_main()

def regression_main():
  os.system('cls||clear')
  print("Linear Regression\n-----------------\n")
  print("1. Test regression works using single patient ID")
  print("2. MDRD vs CKD-EPI all appropriate patients")
  print("3. Regression charts")
  print("4. Patients in each stage of CKD (table)")
  print("5. UPDATE ONLY - Add 2020 prediction")
  print("6. NEW Prediction comparisson table")
  print("ENTER to go back to the main menu")
  selection = input ("\nEnter your choice: ")
  if selection == "1":
    regressionTestOne()
  elif selection == "2":
    #pids = db.patientsSelectSampleCountGreaterThan(2,1)
    pids = db.patientsWithMDRDAndMoreThanNSamples(2)
    linreg.leastSquaresMDRDCKDEPI(pids)
  elif selection == "3":
    regressionPlotOne()
  elif selection == "4":
    #pids = db.patientsWithMDRDAndMoreThanNSamples(2)
    pids = db.regressionPIDs()
    linreg.calculatedCategoryBreakdown(pids)
  elif selection == "5":
    linreg.update2020Prediction()
  elif selection == "6":
    pids = db.regressionPIDs()
    #linreg.predictedCategoryChange2020(pids, "MDRD")
    linreg.predictedCategoryChange2020(pids, "CKD-EPI")
  else:
    program_main()

def regressionPlotOne():
  os.system('cls||clear')
  print("Linear Regression: Plot Regression\n----------------------------------\n")
  print("Enter a known patient ID to plot their regression. Close the chart to continue.")
  selection = input ("\nEnter patient ID: ")
  if selection.isnumeric():
    linreg.getPatientLinearRegression(selection)
  regression_main()

def regressionTestOne():
  os.system('cls||clear')
  print("Linear Regression: Test Regression\n----------------------------------\n")
  print("Enter a known patient ID to plot their regression. Close the chart to continue.")
  selection = input ("\nEnter patient ID: ")
  if selection.isnumeric():
    linreg.regressSingleForTesting(selection)
  regression_main()

def program_main():
  os.system('cls||clear')
  print("MAIN MENU\n------------------------------")
  print("1. CSV Parser")
  print("2. Database Tools")
  print("3. Data modification etc.")
  print("4. Linear Regression")
  print("ENTER to go quit the program")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    csv_main()
  elif selection == "2":
    db_main()
  elif selection == "3":
    data_main()
  elif selection == "4":
    regression_main()
  else: 
    return

if __name__ == '__main__':
  logging.info("Session started")
  program_main()
  logging.info("Session ended\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")