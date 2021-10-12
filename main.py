import csv_parser
import db_methods
import os

def doNothing():
    return True

def specificSearch():
    print("Specific Search")

def mainMenu():
  menu = ""  
  os.system('cls||clear')
  print("CKD Analysis\n------------\n")
  print("1. Process CSV")
  print("2. Specific Search")
  print("----------\n0. Exit")
  menu = input("Pick an option: ")
  fxDict.get(menu, lambda: 'Invalid')()
  if menu != 0:
    mainMenu()
    
fxDict = {
  '1': csv_parser.selectFile,
  '0': doNothing
}

if __name__ == '__main__':
    mainMenu()