$cmdPath = "$env:LOCALAPPDATA\Microsoft\WindowsApps\t6modm.cmd"

if (Test-Path $cmdPath) {
    Remove-Item $cmdPath -Force
}

py make.py
py src\main.py setup