Attribute VB_Name = "Module1"
' Paul Johnson
' paul.johnson54@nhs.net, pjohnson.cv@gmail.com
' September, 2021

' A file processor for anonymising patient identifiers from a TelePath list output
' Written so my workplace supervisor to anonymise vast quantities of data with
' minimal effort.
' - Opens the data, compares the PID against a list held in this workbook
' - Overwrites the data PID with the corresponding study ID
' - Strips out useless rows
' - Saves the file as CSV
' ThisWorkbook also contains OnOpen and AfterSave routines which apply timestamps
' to Cells C14 and C16, to show the user they have saved any updated
' patient_renumber data to the list.

Dim wbMacro As Workbook  ' Set by AnonymiseData()
Dim wbData As Workbook   ' Set by OpenFile()

' Hook for "Browse" button on MAIN sheet
' Displays file dialog with filter set to all files, and default path HFS drive
' Copies the selected file name to E2 on MAIN sheet
Sub BrowseData()
  Set fd = Application.FileDialog(msoFileDialogFilePicker)
  With fd
    .Filters.Clear
    .Filters.Add "All Files", "*.*", 1
    .Title = "Choose a gathered list"
    .AllowMultiSelect = False
    .InitialFileName = "C:\Example\OutDir\" ' Hardcoded path removed, put your own input path here
    If .Show = True Then
      strFile = .SelectedItems(1)
    End If
  End With
  
  If strFile <> "" Then
    Cells(2, 5) = strFile
  Else
    Cells(2, 5) = ""
  End If
End Sub

' Hook for "Anonymise" button on MAIN sheet
' Checks for a path in Cell E2, and calls necessary routines to process the file
Sub AnonymiseData()
  Sheets("MAIN").Cells(15, 3) = Format(Now(), "yy-mm-dd hh:MM:ss")
  Sheets("MAIN").Cells(16, 3) = ""
  
  Set wbMacro = ThisWorkbook
  If Cells(2, 5) = "" Then
    Call MsgBox("No data selected" & vbCrLf & "Click Browse to select a file, then click Anonymise to try again.", vbCritical, "Not Run - No File")
  Else
    If OpenFile(Cells(2, 5)) = True Then
      Call ResetTimer
      Call ReplaceNHS
      Call RemoveUnnecessaryRows
      Call SaveAnonymised
      wbMacro.Sheets("MAIN").Cells(7, 13) = Format(Now(), "hh:MM:ss")
    End If
  End If
End Sub

' Tidy up main worksheet area for displaying progress
' Called by AnonymiseData (button click) rather than on worksheet load in case of
' reusing the button multiple times (as for testing)
Sub ResetTimer()
  wbMacro.Sheets("MAIN").Cells(4, 13) = Format(Now(), "hh:MM:ss")
  wbMacro.Sheets("MAIN").Cells(5, 13) = ""
  wbMacro.Sheets("MAIN").Range("M6:DI6").Interior.Pattern = xlNone
  wbMacro.Sheets("MAIN").Cells(7, 13) = ""
End Sub

' Opens the file specified by the path in E2 on MAIN
' Checks B2 for the string "PJ eGFR Data" which will print if the list is
' correctly formatted
' Returns True if the string is found
Function OpenFile(strPath)
Attribute OpenFile.VB_ProcData.VB_Invoke_Func = " \n14"
  Workbooks.OpenText Filename:=strPath, Origin _
    :=xlMSDOS, StartRow:=1, DataType:=xlDelimited, TextQualifier:= _
    xlDoubleQuote, ConsecutiveDelimiter:=False, Tab:=False, Semicolon:=False _
    , Comma:=False, Space:=False, Other:=True, OtherChar:=";", TrailingMinusNumbers:=True
    
  If Left(Cells(2, 2), 12) = "PJ eGFR Data" Then
    Set wbData = ActiveWorkbook
    ' This stops the data window being shown, allowing a progress bar to be updated
    ' on the main worksheet
    wbData.Windows(1).Visible = False
    OpenFile = True
  Else
    ActiveWindow.Close
    Call MsgBox("Incorrect data in file - Expected 'PJ eGFR Data' from PJMSC list gather." & vbCrLf & "Click Browse to select a file, then click Anonymise to try again.", vbCritical, "Not Run - Wrong Gather")
    OpenFile = False
  End If
End Function

' Copies the NHS number (PID) as a string
' Replaces the value with the output of UpdateStudyID()
' Ignores 8 header rows, processes to last row of usable data
Sub ReplaceNHS()
  iEnd = wbData.Sheets(1).Range("A1048576").End(xlUp).Row
  For i = 9 To iEnd
    percen = Round((100 * ((i - 9) / (iEnd - 9))), 1)
    wbMacro.Sheets("MAIN").Cells(5, 13) = (i - 9) & "/" & (iEnd - 9)
    sNHS = wbData.Sheets(1).Cells(i, 3)
    wbData.Sheets(1).Cells(i, 3) = UpdateStudyID(sNHS)
    wbMacro.Sheets("MAIN").Cells(6, 13 + Round(percen, 0)).Interior.Pattern = xlSolid
    wbMacro.Sheets("MAIN").Cells(6, 13 + Round(percen, 0)).Interior.ColorIndex = 5
  Next
End Sub

' Returns the Study ID (numeric)
' Performs a key-value lookup in patient_renumber using the passed NHS ID as key
' If no key is found, it's added and a study number given as one plus the number
' of rows, which should remain unique unless there is manual intervention.
' When the key is matched or created, the paired value is returned
Function UpdateStudyID(sNHS)
  intStudyID = 0
  
  ' BAD METHOD VERY SLOW SILLY BOY
  '' Loop through key-pair list
  'intLastIDRow = wbMacro.Sheets("patient_renumber").Range("A1048576").End(xlUp).Row
  'For intIDRow = 1 To intLastIDRow
  '  If sNHS = wbMacro.Sheets("patient_renumber").Cells(intIDRow, 1) Then
  '    ' Key found, use value
  '    intStudyID = wbMacro.Sheets("patient_renumber").Cells(intIDRow, 2)
  '    Exit For
  '  End If
  'Next
  
  ' VERSION 2 Correction
  ' Contemplated using custom binary search before recording a macro and fidling with Excels own Find
  ' let Microsoft do the work for me.
  intLastIDRow = wbMacro.Sheets("patient_renumber").Range("A1048576").End(xlUp).Row
  Set wFind = wbMacro.Sheets("patient_renumber").Cells.Find(What:=sNHS, After:=ActiveCell, LookIn:=xlFormulas2, LookAt:= _
        xlWhole, SearchOrder:=xlByColumns, SearchDirection:=xlNext, MatchCase:= _
        False, SearchFormat:=False)
  If Not wFind Is Nothing Then
    intStudyID = wbMacro.Sheets("patient_renumber").Cells(wFind.Row, 2)
  End If
  
  ' This remains untouched in version 2
  If intStudyID = 0 Then
    ' No key found, create new pair
    intStudyID = intLastIDRow + 1
    wbMacro.Sheets("patient_renumber").Cells(intLastIDRow + 1, 1) = sNHS
    wbMacro.Sheets("patient_renumber").Cells(intLastIDRow + 1, 2) = intStudyID
  End If
  
  UpdateStudyID = intStudyID
End Function

' All but the descriptive header row (row 6, standardised output) are irrelevant
' Removing them here makes processing the CSV in python a bit more convenient
Sub RemoveUnnecessaryRows()
  wbData.Sheets(1).Range("1:5,7:8").Delete Shift:=xlUp
End Sub

' Saves the anonymised workbook as a CSV file with a timestamp in the file name
' Closes the data file by disabling excel alerts, immediately re-enables alerts
' Uses SHELL to open the folder, showing the user a file has been created
Sub SaveAnonymised()
  strPath = "C:\Example\InDir" ' Hardcoded path removed, put your own output path here
  strDate = Format(Now(), "yymmdd hhMMss")
  strFile = strDate & " " & wbData.Name
  Call wbData.SaveAs(strPath & strFile, xlCSV)
  
  ' Prevent user being asked to save - don't want them to save this manually
  Application.DisplayAlerts = False
  wbData.Close
  Application.DisplayAlerts = True
  
  Call Shell("C:\WINDOWS\explorer.exe """ & strPath & "", vbNormalFocus)
End Sub
