param(
    [string]$FrontendDir = ".",
    [string]$BackendDir = ".\backend",
    [string]$CommitMessage = "Deploy empire build"
)

$ErrorActionPreference = "Stop"

function Step($msg) {
    Write-Host ""
    Write-Host "=== $msg ===" -ForegroundColor Cyan
}

function Ensure-Command($name, $installHint) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Host "$name not found. $installHint" -ForegroundColor Yellow
        throw "$name is required"
    }
}

function Refresh-NpmPath {
    try {
        $npmPrefix = npm config get prefix
        $npmBin = Join-Path $npmPrefix "node_modules\.bin"
        $userNpm = Join-Path $env:APPDATA "npm"
        $env:Path = "$env:Path;$npmPrefix;$npmBin;$userNpm;C:\Program Files\nodejs"
    } catch {
        $env:Path = "$env:Path;$env:APPDATA\npm;C:\Program Files\nodejs"
    }
}

Step "Move to repo root"
Set-Location "C:\Zerenthis"

Step "Check Git"
Ensure-Command "git" "Install Git first."

Step "Initialize / verify git remote"
if (-not (Test-Path ".git")) {
    git init
}

$remoteExists = git remote 2>$null
if ($remoteExists -notcontains "origin") {
    git remote add origin https://github.com/Temerizen/Zerenthis.git
} else {
    git remote set-url origin https://github.com/Temerizen/Zerenthis.git
}

git branch -M main

Step "Commit and push"
git add .
git commit -m $CommitMessage 2>$null
try {
    git pull origin main --allow-unrelated-histories --no-edit
} catch {
    Write-Host "Pull skipped or had nothing useful to merge." -ForegroundColor DarkYellow
}
git push -u origin main

Step "Check Node / npm"
Ensure-Command "npm" "Install Node.js first."

Step "Install or verify Vercel CLI"
if (-not (Get-Command "vercel" -ErrorAction SilentlyContinue)) {
    npm install -g vercel
    Refresh-NpmPath
}

Step "Install or verify Railway CLI"
if (-not (Get-Command "railway" -ErrorAction SilentlyContinue)) {
    npm install -g @railway/cli
    Refresh-NpmPath
}

Step "Verify CLIs"
Refresh-NpmPath
Ensure-Command "vercel" "Global npm bin is not on PATH yet."
Ensure-Command "railway" "Global npm bin is not on PATH yet."

Step "Deploy frontend to Vercel"
Set-Location (Resolve-Path $FrontendDir)
Write-Host "Vercel may prompt you to log in and confirm project settings." -ForegroundColor Yellow
vercel --prod

Step "Deploy backend to Railway"
Set-Location (Resolve-Path $BackendDir)
Write-Host "Railway may prompt you to log in, link project, and confirm service." -ForegroundColor Yellow
railway login
railway link
railway up

Step "Post-deploy env var checklist"
Write-Host ""
Write-Host "Set these in Railway backend variables:" -ForegroundColor Green
Write-Host "OPENAI_API_KEY=your_key_here"
Write-Host "PUBLIC_BASE_URL=https://YOUR-RAILWAY-DOMAIN"
Write-Host "BASE_URL=https://YOUR-RAILWAY-DOMAIN"

Write-Host ""
Write-Host "If your frontend needs the backend URL, set this in Vercel:" -ForegroundColor Green
Write-Host "VITE_API_URL=https://YOUR-RAILWAY-DOMAIN"

Write-Host ""
Write-Host "Deploy flow finished." -ForegroundColor Green
Write-Host "GitHub repo: https://github.com/Temerizen/Zerenthis" -ForegroundColor Green
