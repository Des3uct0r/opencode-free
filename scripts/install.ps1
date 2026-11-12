param(
    [ValidateSet('all', 'opencode', 'claude', 'codex')]
    [string]$Target = 'all',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repo 'skills\opencode-free'
if (-not (Test-Path (Join-Path $source 'SKILL.md'))) {
    throw "SKILL.md not found at $source"
}

$home_ = $env:USERPROFILE
$destinations = @{
    opencode = Join-Path $home_ '.config\opencode\skills\opencode-free'
    claude   = Join-Path $home_ '.claude\skills\opencode-free'
    codex    = Join-Path $home_ '.agents\skills\opencode-free'
}

function Install-Skill([string]$name, [string]$dest) {
    if ((Test-Path $dest) -and -not $Force) {
        Write-Host "skip   $name (already present: $dest)" -ForegroundColor Yellow
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Copy-Item $source $dest -Recurse -Force
    Write-Host "installed $name -> $dest" -ForegroundColor Green
}

$targets = if ($Target -eq 'all') { @('opencode', 'claude', 'codex') } else { @($Target) }
foreach ($t in $targets) { Install-Skill $t $destinations[$t] }

if ($targets -contains 'opencode') {
    $exe = Get-Command opencode -ErrorAction SilentlyContinue
    if ($exe) {
        Write-Host 'reloading OpenCode...' -ForegroundColor Cyan
        & $exe.Source reload 2>&1 | Select-Object -Last 1
    } else {
        Write-Host 'opencode not on PATH; reload it manually after opening a terminal.' -ForegroundColor Yellow
    }
}

Write-Host ''
Write-Host 'Restart the OpenCode desktop app (if open) so it re-scans skills.'
Write-Host 'Invoke with /opencode-free (OpenCode, Claude Code) or $opencode-free (Codex).'
