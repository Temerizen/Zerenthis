param(
    [string]$Message = "ZERENTHIS MILESTONE SNAPSHOT"
)

Set-Location C:\ZerenthisV2
git add .
git commit -m $Message
git push origin main --force
git status
