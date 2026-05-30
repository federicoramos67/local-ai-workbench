$ErrorActionPreference = "Stop"

$PythonExe = $null
$PythonArgs = @()
$NugetPython = Join-Path $PSScriptRoot ".python_nuget\tools\python.exe"
$LocalPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $NugetPython) {
  $PythonExe = $NugetPython
} elseif (Test-Path $LocalPython) {
  $PythonExe = $LocalPython
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $PythonExe = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $PythonExe = "py"
  $PythonArgs = @("-3")
} else {
  throw "Python 3.11+ was not found. Install Python and try again."
}

function Invoke-Python {
  param([string[]]$Arguments)
  & $PythonExe @PythonArgs @Arguments
}

function Get-PythonValue {
  param([string]$Code)
  $value = & $PythonExe @PythonArgs -c $Code
  if ($LASTEXITCODE -ne 0) {
    throw "Python discovery command failed: $Code"
  }
  return ($value | Select-Object -First 1).Trim()
}

$PythonPrefix = Get-PythonValue "import sys; print(sys.base_prefix)"
$TclRoot = Join-Path $PythonPrefix "tcl"
$TclLibrary = Join-Path $TclRoot "tcl8.6"
$TkLibrary = Join-Path $TclRoot "tk8.6"
$HooksDir = Join-Path $PSScriptRoot "hooks"

if (-not (Test-Path $TclLibrary)) { throw "Missing Tcl library folder: $TclLibrary" }
if (-not (Test-Path $TkLibrary)) { throw "Missing Tk library folder: $TkLibrary" }

$env:TCL_LIBRARY = $TclLibrary
$env:TK_LIBRARY = $TkLibrary
$env:LOCAL_AI_WORKBENCH_PYTHON_ROOT = $PythonPrefix
$env:LOCAL_AI_WORKBENCH_TCL_ROOT = $TclRoot

$CommonPyInstallerArgs = @(
  "-m", "PyInstaller",
  "--noconfirm",
  "--clean",
  "--windowed",
  "--onefile",
  "--hidden-import=tkinter",
  "--hidden-import=tkinter.ttk",
  "--hidden-import=tkinter.filedialog",
  "--hidden-import=tkinter.messagebox",
  "--hidden-import=customtkinter",
  "--hidden-import=_tkinter",
  "--additional-hooks-dir", $HooksDir,
  "--collect-all", "customtkinter",
  "--add-data", "$TclLibrary;_tcl_data",
  "--add-data", "$TkLibrary;_tk_data"
)

Write-Host "Cleaning previous build artifacts..."
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue

Write-Host "Building English executable..."
Invoke-Python @(
  $CommonPyInstallerArgs +
  "--name", "LocalAIWorkbench_EN",
  "main.py"
)

Write-Host "Building Spanish executable..."
Invoke-Python @(
  $CommonPyInstallerArgs +
  "--name", "BancoIA_ES",
  "main_es.py"
)

Write-Host "Verifying executables..."
$en = Join-Path $PSScriptRoot "dist\LocalAIWorkbench_EN.exe"
$es = Join-Path $PSScriptRoot "dist\BancoIA_ES.exe"

if (-not (Test-Path $en)) { throw "Missing LocalAIWorkbench_EN.exe" }
if (-not (Test-Path $es)) { throw "Missing BancoIA_ES.exe" }

$enProcess = Start-Process -FilePath $en -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3
if (-not $enProcess.HasExited) {
  Stop-Process -Id $enProcess.Id -Force
  Write-Host "LocalAIWorkbench_EN.exe launched successfully."
} elseif ($enProcess.ExitCode -ne 0) {
  throw "LocalAIWorkbench_EN.exe exited with code $($enProcess.ExitCode)"
}

$esProcess = Start-Process -FilePath $es -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 3
if (-not $esProcess.HasExited) {
  Stop-Process -Id $esProcess.Id -Force
  Write-Host "BancoIA_ES.exe launched successfully."
} elseif ($esProcess.ExitCode -ne 0) {
  throw "BancoIA_ES.exe exited with code $($esProcess.ExitCode)"
}

Write-Host "Done. Executables are in the dist folder."
