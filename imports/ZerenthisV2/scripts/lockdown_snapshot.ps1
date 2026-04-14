param(
    [string]$Message = "Z-COSMOS LOCKDOWN MILESTONE"
)

Set-Location C:\ZerenthisV2

.\scripts\repair_state.ps1

git add .
git commit -m $Message
git push origin main --force
git status
