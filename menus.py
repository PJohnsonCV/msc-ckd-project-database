import csv_parser as csv
import db_methods as db
import data_manip as customs
import os
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(levelname)s | %(message)s', level=logging.DEBUG)

def csv_main():
  os.system('cls||clear')
  print("CSV Parser\n----------\n")
  print("1. Import full")
  print("ENTER to go back to the main menu")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    csv.selectFile(0)
  elif selection == "2":
    csv.selectFile(1)
  elif selection == "3":
    csv.selectFile(2)
  program_main()

def db_main():
  os.system('cls||clear')
  print("Database Control\n----------------\n")
  print("1. Reset/Initialise")
  print("2. Alter Tables")
  print("3. Any custom fixes to run after reset/alter.")
  print("ENTER to go back to the main menu")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    resetPanic()
  elif selection == "2":
    db.alterDatabase()
  elif selection == "3":
    #input("No custom fixes to run")
    #db.initialiseAnalytes()
    #customs.insertSampleAges()
    customs.insertCalculatedEGFR()
  program_main()

def resetPanic():
  os.system('cls||clear')
  print("Database Control: RESET DATABASE\n--------------------------------\n\n")
  print("! ----------------------- !!! WARNING !!! ----------------------- !\n")
  print("! Resetting the database will result in TOTAL DATA LOSS.          !\n")
  print("! Do NOT reset without due cause, and a backup of necessary data. !\n")
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
        input("\nYou have reset the database. Press return to continue.")
        db_main()
    input("\nDatabase was NOT reset because you cancelled or didn't pass a check. Press return to go back to the menu.\n")
    db_main()

def data_main():
  os.system('cls||clear')
  print("Data modification etcetra\n-------------------------\n")
  print("1. Add ordinal age to samples")
  print("2. Add MDRD and CKD-EPI calculations to results")
  print("ENTER to go back to the main menu")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    print()
  program_main()

def program_main():
  os.system('cls||clear')
  print("MAIN MENU\n---------")
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
  else: 
    return

if __name__ == '__main__':
  logging.info("Session started")
  program_main()
  logging.info("Session ended\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")