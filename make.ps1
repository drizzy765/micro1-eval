# PowerShell helper for a weak Windows laptop. Run from the repo root:
#   .\make.ps1 setup
#   .\make.ps1 test
#   .\make.ps1 baseline
param(
    [Parameter(Position = 0)]
    [ValidateSet("setup", "generate", "test", "baseline", "help")]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Ensure-Venv {
    if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
        python -m venv .venv
    }
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

switch ($Target) {
    "setup" {
        Ensure-Venv
        Write-Host "venv ready. Next: .\.venv\Scripts\Activate.ps1"
    }
    "generate" {
        & .\.venv\Scripts\python.exe -m generator.write_assets
    }
    "test" {
        & .\.venv\Scripts\python.exe -m pytest -q
    }
    "baseline" {
        & .\.venv\Scripts\python.exe -m runner.run --backend baseline --runs 1
    }
    default {
        Write-Host "Targets: setup, generate, test, baseline"
    }
}
