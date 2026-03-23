Dim scriptPath, batchPath
scriptPath = WScript.ScriptFullName
batchPath = Left(scriptPath, InStrRev(scriptPath, "\")) & "SYSTEM_browser.bat"

CreateObject("WScript.Shell").Run """" & batchPath & """", 0, False
