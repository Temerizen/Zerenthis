$ErrorActionPreference = "Stop"

$autonomyDir = "backend\data\autonomy"
$historyPath = Join-Path $autonomyDir "cycle_history.jsonl"
$reflectionPath = Join-Path $autonomyDir "reflection_summary.json"

if (!(Test-Path $historyPath)) {
    throw "Missing cycle history: $historyPath"
}

$lines = Get-Content $historyPath | Where-Object { $_.Trim() -ne "" }
$entries = @()

foreach ($line in $lines) {
    try {
        $entries += ($line | ConvertFrom-Json)
    } catch {
    }
}

if ($entries.Count -eq 0) {
    throw "No readable entries found in cycle history."
}

$total = $entries.Count
$successes = @($entries | Where-Object { $_.ok -eq $true }).Count
$failures = @($entries | Where-Object { $_.ok -eq $false }).Count
$latest = $entries[-1]

$recentWindow = 25
if ($total -lt $recentWindow) { $recentWindow = $total }
$recent = @($entries | Select-Object -Last $recentWindow)
$recentSuccesses = @($recent | Where-Object { $_.ok -eq $true }).Count
$recentFailures = @($recent | Where-Object { $_.ok -eq $false }).Count

$continuitySeen = @($entries | Where-Object { $null -ne $_.continuity }).Count
$brainSeen = @($entries | Where-Object { $null -ne $_.brain }).Count
$healthSeen = @($entries | Where-Object { $null -ne $_.health }).Count

$assessment = if ($failures -eq 0 -and $total -ge 300) {
    "stable_persistent_autonomy_confirmed"
} elseif ($failures -eq 0) {
    "stable_autonomy_observed"
} elseif ($failures -le 2) {
    "mostly_stable_minor_faults"
} else {
    "instability_detected"
}

$nextRecommendation = switch ($assessment) {
    "stable_persistent_autonomy_confirmed" { "safe_to_add_self_model_summary_or_goal_persistence" }
    "stable_autonomy_observed" { "increase_runtime_then_retest" }
    "mostly_stable_minor_faults" { "fix_faults_before_expansion" }
    default { "stabilize_core_before_any_new_layer" }
}

$reflection = [ordered]@{
    generated_at = (Get-Date).ToString("o")
    total_cycles_observed = $total
    successes = $successes
    failures = $failures
    recent_window = $recentWindow
    recent_successes = $recentSuccesses
    recent_failures = $recentFailures
    health_observed_cycles = $healthSeen
    brain_observed_cycles = $brainSeen
    continuity_observed_cycles = $continuitySeen
    latest_cycle = $latest.cycle
    latest_ok = $latest.ok
    latest_error = $latest.error
    assessment = $assessment
    next_recommendation = $nextRecommendation
}

$reflection | ConvertTo-Json -Depth 10 | Set-Content $reflectionPath -Encoding UTF8
Write-Host "=== REFLECTION SUMMARY ===" -ForegroundColor Cyan
Get-Content $reflectionPath
