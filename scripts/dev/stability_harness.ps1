param(
    [int]$Cycles = 60,
    [int]$DelayMs = 1500,
    [int]$MaxConsecutiveErrors = 3
)

$ErrorActionPreference = "Stop"
$logPath = "backend\data\stability\stability_log.jsonl"
$summaryPath = "backend\data\stability\stability_summary.json"

if (Test-Path $logPath) { Remove-Item $logPath -Force }
if (Test-Path $summaryPath) { Remove-Item $summaryPath -Force }

$ok = 0
$fail = 0
$consecutive = 0
$started = Get-Date
$stopReason = "completed"

for ($i = 1; $i -le $Cycles; $i++) {
    $entry = [ordered]@{
        cycle = $i
        time = (Get-Date).ToString("o")
        health_ok = $false
        brain_ok = $false
        continuity_ok = $false
        error = $null
    }

    try {
        $health = Invoke-RestMethod http://127.0.0.1:8000/health
        $entry.health_ok = $true

        $brain = Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/brain/run
        $entry.brain_ok = $true

        try {
            $continuity = Invoke-RestMethod http://127.0.0.1:8000/api/continuity/state
            $entry.continuity_ok = $true
        } catch {
            $entry.continuity_ok = $false
        }

        $ok++
        $consecutive = 0
        Write-Host ("PASS {0}/{1}" -f $i, $Cycles) -ForegroundColor Green
    }
    catch {
        $fail++
        $consecutive++
        $entry.error = $_.Exception.Message
        Write-Host ("FAIL {0}/{1} :: {2}" -f $i, $Cycles, $_.Exception.Message) -ForegroundColor Red

        if ($consecutive -ge $MaxConsecutiveErrors) {
            $stopReason = "max_consecutive_errors"
            ($entry | ConvertTo-Json -Compress) | Add-Content $logPath
            break
        }
    }

    ($entry | ConvertTo-Json -Compress) | Add-Content $logPath
    Start-Sleep -Milliseconds $DelayMs
}

$finished = Get-Date
$summary = [ordered]@{
    started_at = $started.ToString("o")
    finished_at = $finished.ToString("o")
    duration_seconds = [math]::Round(($finished - $started).TotalSeconds, 2)
    cycles_requested = $Cycles
    passes = $ok
    fails = $fail
    stop_reason = $stopReason
    log_path = $logPath
}

$summary | ConvertTo-Json -Depth 6 | Set-Content $summaryPath -Encoding UTF8
Write-Host ""
Write-Host "=== STABILITY SUMMARY ===" -ForegroundColor Cyan
Get-Content $summaryPath
