import csv_parser as csv
import db_methods as db
import os
import logging
logging.basicConfig(filename='study.log', encoding='utf-8', format='%(asctime)s: %(levelname)s | %(message)s', level=logging.DEBUG)

def csv_main():
  os.system('cls||clear')
  print("CSV Parser\n----------\n")
  print("1. Import full")
  print("2. Import patient IDs")
  print("3. Import sample results")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    csv.selectFile(0)
  elif selection == "2":
    csv.selectFile(1)
  elif selection == "3":
    csv.selectFile(2)
  else: 
    program_main()

def db_main():
  os.system('cls||clear')
  print("Database Control\n----------------\n")
  print("1. Reset/Initialise")
  print("2. ")
  print("Any other key to go back to main menu")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    db.resetDatabase()
  else: 
    program_main()

def program_main():
  os.system('cls||clear')

  print("1. CSV Parser")
  print("2. Database Tools")
  print("3. Linear Regression")
  print("Any other key to exit the program")
  selection = input("\nEnter your choice: ")
  if selection == "1":
    csv_main()
  elif selection == "2":
    db_main()
  else: 
    return

if __name__ == '__main__':
  logging.info("Session started")
  program_main()
  logging.info("Session ended\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")