# pull_from_pythonanywhere.ps1

$PA_USER     = "amcgrean"
$PA_HOST     = "ssh.pythonanywhere.com"

$REMOTE_ROOT = "/home/amcgrean/mysite"
$REMOTE_DB   = "/home/amcgrean/mysite/bids.db"

$LOCAL_ROOT  = "C:\Users\amcgrean\python\pa-bid-request"

New-Item -ItemType Directory -Force -Path $LOCAL_ROOT | Out-Null

Write-Host "== Pulling code from PythonAnywhere =="
scp -r "${PA_USER}@${PA_HOST}:${REMOTE_ROOT}/*" "${LOCAL_ROOT}\"

Write-Host "== Pulling DB file =="
scp "${PA_USER}@${PA_HOST}:${REMOTE_DB}" "${LOCAL_ROOT}\bids.db"

Write-Host "== Done =="
Write-Host "Local project: $LOCAL_ROOT"
