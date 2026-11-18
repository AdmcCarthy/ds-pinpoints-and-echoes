# Rebuild every extract in story/data/, in dependency order (field before cascade, cascade before money and test).
# Paths default to the sibling checkouts and the local Volve archive; override them with the parameters.
param(
    [string]$Ep = "..\ep_geoscience_analytics",
    [string]$Volve = "C:\appl\Volve",
    [string]$Surfaces = "..\kit-surfaces"
)
$ErrorActionPreference = "Stop"
$py = Join-Path $Ep ".venv\Scripts\python.exe"
$steps = @(
    @("make_wells.py", @()),
    @("make_core.py", @()),
    @("make_log.py", @("--volve", $Volve)),
    @("make_seismic.py", @("--volve", $Volve)),
    @("make_field.py", @("--volve", $Volve, "--surfaces", $Surfaces)),
    @("make_cascade.py", @()),
    @("make_money.py", @()),
    @("make_test.py", @())
)
foreach ($s in $steps) {
    Write-Host "== $($s[0])"
    & $py -I (Join-Path $PSScriptRoot $s[0]) --ep $Ep @($s[1]) | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "$($s[0]) failed" }
}
