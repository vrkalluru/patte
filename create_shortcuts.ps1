$WshShell = New-Object -ComObject WScript.Shell

$Target = "$env:LOCALAPPDATA\Programs\Patte\Patte.exe"
$WorkDir = "$env:LOCALAPPDATA\Programs\Patte"
$Icon = "$env:LOCALAPPDATA\Programs\Patte\_internal\assets\icon.ico"

$Desktop = [System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Patte.lnk')
$StartMenu = [System.IO.Path]::Combine([Environment]::GetFolderPath('ApplicationData'), 'Microsoft\Windows\Start Menu\Programs\Patte.lnk')

foreach ($Path in @($Desktop, $StartMenu)) {
    $Shortcut = $WshShell.CreateShortcut($Path)
    $Shortcut.TargetPath = $Target
    $Shortcut.WorkingDirectory = $WorkDir
    if (Test-Path $Icon) {
        $Shortcut.IconLocation = $Icon
    }
    $Shortcut.Description = "Patte Voice Dictation"
    $Shortcut.Save()
    Write-Output "Created shortcut at $Path pointing to $Target"
}
