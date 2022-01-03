# ckd-analysis
A python program to use data parsed from CSV files and stored in a local SQLite DB, to produce graphical output of biochemical and haematological parameters to visualise a model for generating alerts of at-risk patients of deteriorating CKD.

## CSV requirements
The following fields are listed in expected order, with data type and formatting requirements. It is advised to look at the example file and csv_parser.py to understand the requirements.

Date sample received by lab     dd.mm.yy
Time sample received by lab     hh:mm
Patient study identifier        integer
Sample ID as given by lab       X.YY,0000000.Z where X is Q or W, Z is a check digit (letter) for the 7 digit ID
Sex	                            M or F
DOB/Age                         dd.mm.yy or dd-mm-yy (if close to 100 years)
Location                        string
Location Group                  string
14 x numeric fields for analyte results:
Sodium, Potassium, Urea, Creatinine, eGFR, AKI, Urine microalbumin ratio, CRP, HBA1c, HBA1c (yes), Haemoglobin, Haematocrit, MCH, Phosphate

## STYLE GUIDE
* Methods in camelCase
* Variables in lower_case
* SQL reserved words in UPPERCASE, tables/variables etc. in lowercase
