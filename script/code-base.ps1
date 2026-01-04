# --- Import utility functions
$utilsPath = "/home/atari-monk/atari-monk/project/access-guard/script/utils.ps1"
if (Test-Path $utilsPath) {
    . $utilsPath  # dot-source the script to load functions
} else {
    Write-Error "Utils script not found at $utilsPath"
}

# --- Paths
$proj = "/home/atari-monk/atari-monk/project/access-guard"

snippet clear

# --- Project structure
if (Test-Path $proj) {
    fstree $proj -c
    snippet -d 'Project Structure:' -t context
}

# --- Project files
snippet -c 'Project Code Base:' -t context
$files = Get-PyProjFiles $proj
foreach ($file in $files) {
    snippet -f $file -t context
}

# --- Prompt for Swagger
$prompt = "Prepare step by step, copy paste, best you know how, implementation of swagger for this project"
snippet -c $prompt -t prompt

snippet pop
