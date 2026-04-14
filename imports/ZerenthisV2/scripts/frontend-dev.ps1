Set-Location $PSScriptRoot\..
if (!(Test-Path .\frontend\node_modules)) {
    Set-Location .\frontend
    npm install
} else {
    Set-Location .\frontend
}
npm run dev
