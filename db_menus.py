import db_methods
from os import system
from sys import exit

def dbMenu():
  system('cls||clear')
  print("INSPECT DATABASE\n----------------\n")
  print("1: Table counts")
  print("2: Patient queries")
  print("3: Sample queries")
  print("4: Test queries")
  print("R: Reset Database")

  print("9. Quit")
  selection = input("\nPick a number (1 - 6), or 'R': ")

  # Developed in VSCode using Python 3.9.2, no match-case available
  if selection == '1':
    db_methods.displayTableRowCount()
    dbMenu()
  elif selection == '2':
    patientMenu()
    dbMenu()
  elif selection == '3':
    sampleMenu()
  elif selection == '4':
    testMenu()
  elif selection == '5':
    db_methods.initialiseTables()
    exit()
  elif selection.upper() == "R":
    resetMenu()
  else:
    exit()

def resetMenu():
  system('cls||clear')
  print("RESET DATABASE\n--------------\n\n")
  print("! ----------------------- !!! WARNING !!! ----------------------- !\n")
  print("! Resetting the database will result in total data loss.          !\n")
  print("! Do NOT reset without due cause, and a backup of necessary data. !\n")
  print("! ----------------------- !!! WARNING !!! ----------------------- !\n\n")
  selection = input("Type 'QUIT' to go back to the db_menu, or 'CONT' to continue with a reset: ")
  if selection.upper() == "QUIT":
    dbMenu()
  elif selection.upper() == "CONT":
    print("\nTo confirm you want to reset the database, type the following message: \n")
    confirm = input("I WANT TO RESET THE DATABASE\n")
    if confirm.upper() == "I WANT TO RESET THE DATABASE":
      dblconfirm = input("\nAre you sure? Y/N: ")
      if dblconfirm.upper() == "Y":
        db_methods.resetDatabase()
        input("\nYou have reset the database. Press return to continue.")
        dbMenu()
    input("\nDatabase was NOT reset because you cancelled or didn't pass a check. Press return to go back to the menu.\n")
    dbMenu()

def patientMenu():
  system('cls||clear')
  print("INSPECT Patient\n----------------\n")
  print("1: View patient details")
  print("2: View samples for a patient")
  print("3: View samples for a patient (date range)")
  selection = input("\nPick a number (1 - ): ")

  if selection == '1':
    patient_id = input("\nEnter a patient ID: ")
    db_methods.printPatientDetails(patient_id)
    patientMenu()
  elif selection == '2':
    patient_id = input("\nEnter a patient ID: ")
    db_methods.printPatientSamples(patient_id,1)
    patientMenu()
  elif selection == '3':
    patient_id = input("\nEnter a patient ID: ")
    date_from = input("Enter from date (YYYY-MM-DD): ")
    date_to = input("Enter to date (YYYY-MM-DD):   ")
    db_methods.printPatientSamples(patient_id,2,date_from, date_to)
    input()
    patientMenu()
  #else:
    #exit()

def sampleMenu():
  system('cls||clear')
  print("INSPECT Sample\n----------------\n")
  print("1: View sample results (RAW)")
  print("2: Patient blood results (formatted)")
  print("3: Back to database menu")
  selection = input("\nPick a number (1 - ): ")

  if selection == "1":
    sample_id = input("\nEnter a sample number: ")
    db_methods.printSampleResults(sample_id)
  elif selection == "2":
    sample_id = input("\nEnter a patient ID number: ")
    db_methods.printPatientResults(sample_id)
  elif selection == "3":
    dbMenu()
  sampleMenu()

def testMenu():
  print("Test menu")

if __name__ == '__main__':
  dbMenu()