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

  print("6. Quit")
  selection = input("\nPick a number (1 - 6): ")

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
  else:
    exit()

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
    patientMenu()
  #else:
    #exit()

def sampleMenu():
  print("Sample menu")

def testMenu():
  print("Test menu")

if __name__ == '__main__':
  dbMenu()