import os
import sys
import csv_parser

def mainMenu():
  os.system('cls||clear')
  print("MAIN MENU\n---------\n\n")
  print("1: Import new CSV file\n   (Explainer)")
  print("2: Generate images")
  print("3: Inspect database")
  print("4. Exit")
  selection = input("\nPick a number (1 - 4):")
  
  # Replace with a match-case statement if running python 3.10
  # VSCode using 3.9.2 interpreter at time of development
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

  #if (type(selection) is not int):
  #  mainMenu()
  #match int(se1lection):
  #  case 1: print("Selected 1")
  #  case 2: print("Selected 2")
  #  case 3: print("Selected 3")
  #  case 4: sys.exit()
    

if __name__ == '__main__':
    mainMenu() 