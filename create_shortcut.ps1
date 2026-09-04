$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$Shortcut = $WshShell.CreateShortcut("$Desktop\Kohisar Model School (KMS).lnk")
$Shortcut.TargetPath = "$PSScriptRoot\kms_run.bat"
$Shortcut.WorkingDirectory = "$PSScriptRoot"
$Shortcut.Description = "Kohisar Model School & College ERP Portal"
$Shortcut.Save()
Write-Host "[OK] Shortcut created successfully on Desktop!"
