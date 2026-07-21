# run_erp_sync.ps1 — orchestrates import_data.py with retries, logs, and robust .env loading
param(
    [int]$MaxRetries = 3
)

$ErrorActionPreference = 'Stop'

# --- Resolve repo root (folder containing this script) ---
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = $ScriptDir

# --- Paths ---
$PythonVenv = Join-Path $Repo ".venv\Scripts\python.exe"
if (Test-Path $PythonVenv) { 
    $Python = $PythonVenv 
    Write-Host "[INFO] Found virtual environment at $Python" -ForegroundColor Cyan
}
else { 
    $Python = "python" 
    Write-Host "[WARNING] .venv not found. Falling back to system '$Python'. This may fail." -ForegroundColor Yellow
}

$LogDir = Join-Path $Repo "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Force -Path $LogDir | Out-Null }
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "erp_sync_$Stamp.log"

# --- Load .env into current process ---
function Load-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }

    Get-Content -Raw -Path $Path |
    Select-String -Pattern '^(?!\s*#)(.+)$' -AllMatches |
    ForEach-Object { $_.Matches.Value } |
    ForEach-Object {
        $kv = $_ -split '=', 2
        if ($kv.Count -lt 2) { return }
        $k = $kv[0].Trim()
        $v = $kv[1].Trim()

        if ($v -match '^"(.*)"$') { $v = $Matches[1] }
        elseif ($v -match "^'(.*)'$") { $v = $Matches[1] }
            
        # Simple expansion for common Windows vars if needed
        $v = $v.Replace("${HOME}", $env:USERPROFILE).Replace("$HOME", $env:USERPROFILE)

        Set-Item -Path ("Env:{0}" -f $k) -Value $v
    }
}

$env:PYTHONUNBUFFERED = "1"
$DotEnv = Join-Path $Repo ".env"
Load-DotEnv -Path $DotEnv

# --- Run import_data.py with retries ---
"Starting Beisser ERP Sync at $(Get-Date -Format o)" | Tee-Object -Append -FilePath $LogFile

$attempt = 0
do {
    $attempt++
    "Attempt $attempt :: $(Get-Date -Format o)" | Tee-Object -Append -FilePath $LogFile

    $args = @((Join-Path $Repo "project\import_data.py"))

    try {
        & $Python @args 2>&1 | Tee-Object -Append -FilePath $LogFile
        $code = $LASTEXITCODE
    }
    catch {
        $_ | Out-String | Tee-Object -Append -FilePath $LogFile | Out-Null
        $code = 1
    }

    if ($code -eq 0) {
        "Success :: $(Get-Date -Format o)" | Tee-Object -Append -FilePath $LogFile
        exit 0
    }

    if ($attempt -lt $MaxRetries) {
        $delay = [math]::Pow(2, $attempt)
        "Failed (exit $code). Retrying in $delay sec..." | Tee-Object -Append -FilePath $LogFile
        Start-Sleep -Seconds $delay
    }
} while ($attempt -lt $MaxRetries)

"All retries failed (last exit $code) :: $(Get-Date -Format o)" | Tee-Object -Append -FilePath $LogFile
exit $code
