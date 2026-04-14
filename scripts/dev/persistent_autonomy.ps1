param(
    [int]$Cycles = 300,
    [int]$DelayMs = 1500,
    [int]$MaxConsecutiveErrors = 5
)

$ErrorActionPreference = "Stop"

$dir = "backend\data\autonomy"
New-Item -ItemType Directory -Force $dir | Out-Null

$logPath = Join-Path $dir "cycle_history.jsonl"
$statusPath = Join-Path $dir "latest_status.json"
$summaryPath = Join-Path $dir "run_summary.json"

$started = Get-Date
$passes = 0
$fails = 0
$consecutiveErrors = 0
$bestStreak = 0
$currentStreak = 0
$stopReason = "completed"

for ($i = 1; $i -le $Cycles; $i++) {
    $entry = [ordered]@{
        cycle = $i
        started_at = (Get-Date).ToString("o")
        ok = $false
        health = $null
        brain = $null
        continuity = $null
        error = $null
        streak = $currentStreak
    }

    try {
        $health = Invoke-RestMethod http://127.0.0.1:8000/health
        $brain = Invoke-RestMethod -Method POST http://127.0.0.1:8000/api/brain/run
        $continuity = Invoke-RestMethod http://127.0.0.1:8000/api/continuity/state

        $passes++
        $currentStreak++
        if ($currentStreak -gt $bestStreak) { $bestStreak = $currentStreak }
        $consecutiveErrors = 0

        $entry.ok = $true
        $entry.health = $health
        $entry.brain = $brain
        $entry.continuity = $continuity
        $entry.streak = $currentStreak

        Write-Host ("PASS {0}/{1} | streak={2}" -f $i, $Cycles, $currentStreak) -ForegroundColor Green
    }
    catch {
        $fails++
        $consecutiveErrors++
        $currentStreak = 0

        $entry.ok = $false
        $entry.error = $_.Exception.Message
        $entry.streak = $currentStreak

        Write-Host ("FAIL {0}/{1} | consecutive={2} | {3}" -f $i, $Cycles, $consecutiveErrors, $_.Exception.Message) -ForegroundColor Red

        if ($consecutiveErrors -ge $MaxConsecutiveErrors) {
            $stopReason = "max_consecutive_errors"
            ($entry | ConvertTo-Json -Depth 12 -Compress) | Add-Content $logPath
            break
        }
    }

    ($entry | ConvertTo-Json -Depth 12 -Compress) | Add-Content $logPath

    $status = [ordered]@{
        status = if ($entry.ok) { "ok" } else { "error" }
        current_cycle = $i
        cycles_requested = $Cycles
        passes = $passes
        fails = $fails
        current_streak = $currentStreak
        best_streak = $bestStreak
        consecutive_errors = $consecutiveErrors
        last_started_at = $entry.started_at
        last_error = $entry.error
        log_path = $logPath
    }

    $status | ConvertTo-Json -Depth 12 | Set-Content $statusPath -Encoding UTF8
    Start-Sleep -Milliseconds $DelayMs
}

$finished = Get-Date
$summary = [ordered]@{
    started_at = $started.ToString("o")
    finished_at = $finished.ToString("o")
    duration_seconds = [math]::Round(($finished - $started).TotalSeconds, 2)
    cycles_requested = $Cycles
    passes = $passes
    fails = $fails
    best_streak = $bestStreak
    stop_reason = $stopReason
    log_path = $logPath
    status_path = $statusPath
}

$summary | ConvertTo-Json -Depth 12 | Set-Content $summaryPath -Encoding UTF8

Write-Host ""
Write-Host "=== AUTONOMY SUMMARY ===" -ForegroundColor Cyan
Get-Content $summaryPath
