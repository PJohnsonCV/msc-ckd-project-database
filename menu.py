import os
import sys
import csv_parser

def mainMenu():
  os.system('cls||clear')
  print("MAIN MENU\n---------\n\n")
  print("1: Import new CSV file")
  print("2: Generate images")
  print("3: Inspect database")
  print("4. Exit")
  selection = input("\nPick a number (1 - 4):")
  
  # Developed in VSCode using Python 3.9.2, no match-case available
  if selection == '1':
    csv_parser.selectFile()
    mainMenu()
  elif selection == '2':
    print ("Selected 2")
  elif selection == '3':
    print ("Selected 3")
  elif selection == '4':
    sys.exit()
  else:
    mainMenu()

if __name__ == '__main__':
    mainMenu() 