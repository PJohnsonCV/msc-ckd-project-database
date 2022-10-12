Attribute VB_Name = "Module2"
Sub V2Patch()
  bFoundSheet = False
  For i = 1 To Sheets.Count
    If Sheets(i).Name = "patient_renumber" Then
      bFoundSheet = True
      Exit For
    End If
  Next
  
  If bFoundSheet = False Then
    Call MsgBox("Please select the version 1 Anonymiser in the next window that opens. You will see a box saying 'Success' if patch is successful.", vbCritical, "Version 2 Patcher")
    
    Set fdg = Application.FileDialog(msoFileDialogFilePicker)
    With fdg
      .Filters.Clear
      .Filters.Add "All Files", "*.xlsm", 1
      .Title = "Pick the version 1 Anonymiser you have been using"
      .AllowMultiSelect = False
      .InitialFileName = ""
      If .Show = True Then
        strFile = .SelectedItems(1)
      End If
    End With
    
    If strFile <> "" Then
      Workbooks.Open Filename:=strFile
      Sheets("patient_renumber").Copy After:=Workbooks("Anonymiser_Version2.xlsm").Sheets(1)
      Sheets("patient_renumber").Copy After:=Workbooks("Anonymiser_Version2.xlsm").Sheets(2)
      Windows("Anonymiser.xlsm").Close SaveChanges:=False
      Windows("Anonymiser_Version2.xlsm").Activate
      Sheets("MAIN").Select
      Call MsgBox("There should now be two sheets 'patient_renumber' and 'patient_renumber (2)'. If so, please SAVE now and restart Excel.", vbInformation, "Success...?")
    Else
      MsgBox ("Patch not run, Version 1 file not selected")
    End If
  End If
End Sub
