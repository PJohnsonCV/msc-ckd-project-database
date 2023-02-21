# MSc CKD Project Database
A python program to import and manipulate data parsed from CSV files in a SQLite database. Written for my MSc project and highly bespoke to the needs of said project, this is not the pinacle of database schema design (good intentions fell by the wayside in favor of simplified queries), nor software development (its held together with tape and best intentions), but I was able to get data I needed, and that's all that mattered at the time. 
The project title "A Model to Identify and Method of Graphically Reporting Patients at Risk of End Stage Renal Disease to Primary Care Clinicians" hints at machine learning, but there is none here, this was effectively a manual process of analysing basic linear regression. 

## Dependencies
sqlite3
matplotlib
SciPy
NumPy (apparently?)

## Usage
Start with menus.py, from there the functions can essentialy be divided into data import, data transformation, and data collection. 
From menus.py: 
* CSV Parser provides the methods for importing data to the database, 
* Database Tools gives an overview of table sizes, and options to reset the database if needed 
* Data Modification is calling functions written and removed as I needed them, such as 'Random IDs from 2020'
* Linear Regression has the functions to produce matplotlib charts, perform the lr and more
* Data Analysis and 2020 format have no options, don't select these!
* ~* Hidden menus exist *~ 

## CSV Parser
Please check the comments to understand this otherwise self-explanatory module: parses CSV files for importing data to the database.
### Required file format
The CSV parser reads the output of the Anonymiser macro (also included in this repository). For reference the headers look like this:
*Date Rec'd,Time Rec'd,Hospital No.,Lab No/Spec No,Sex,DOB/Age,LOC,MSG,Sodium,POT,Urea,CRE,eGFR,AKI,UMICR,CRP,IHBA1C,HbA1c,Hb,HCT,MCH,PHO
Results immediately follow. The anonymiser removes a lot of unnecessary header rows so the parser is NOT expecting a normal TelePath gather output file.

## Notes for code reviewers
I learned python for this project! Its not the neatest codebase, and possibly not the most efficient. I'm most proud of my CSV Parser-DB connection and getting import times down from days to seconds with better queries, indexes etc. You can probably tell where the madness / pressure / worry kicks in, as the db_methods db_strings and data_manip modules become more unhinged the closer I get to particular deadlines. 
