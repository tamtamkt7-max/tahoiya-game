param(
    [Parameter(Mandatory = $true)]
    [string]$LocalPath,

    [string]$Remote = "origin",
    [string]$ExpectedRemoteSlug = "",
    [string]$BranchPrefix = "pseudo-codex-bootstrap",
    [switch]$TestMode
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    $output = & git @Args 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed:`n$($output -join [Environment]::NewLine)"
    }
    return @($output)
}

function Assert-NoSensitivePaths {
    $paths = @(Invoke-Git ls-files -co --exclude-standard)
    $blocked = @()
    foreach ($raw in $paths) {
        $p = ($raw -replace '\\', '/').Trim()
        if (-not $p) { continue }
        if ($p -match '(^|/)\.env($|\.)' -and $p -notmatch '(^|/)\.env\.(example|sample|template)$') { $blocked += $p; continue }
        if ($p -match '(^|/)(credentials|client_secret)([^/]*)\.json$') { $blocked += $p; continue }
        if ($p -match '(^|/)service[-_]?account([^/]*)\.json$') { $blocked += $p; continue }
        if ($p -match '(^|/)id_rsa([^/]*)$') { $blocked += $p; continue }
        if ($p -match '\.(pem|p12|pfx|key)$') { $blocked += $p; continue }
    }
    if ($blocked.Count -gt 0) {
        throw "Sensitive-looking files detected. Nothing was pushed:`n$($blocked -join [Environment]::NewLine)"
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not available in PATH."
}

$resolved = (Resolve-Path -LiteralPath $LocalPath).Path
Push-Location $resolved
try {
    Invoke-Git rev-parse --is-inside-work-tree | Out-Null
    $remoteUrl = (Invoke-Git remote get-url $Remote | Select-Object -First 1).Trim()

    if (-not $TestMode) {
        if ($remoteUrl -notmatch 'github\.com[:/]') {
            throw "Remote '$Remote' is not a GitHub remote: $remoteUrl"
        }
        if ($ExpectedRemoteSlug) {
            $normalized = $remoteUrl -replace '\.git$',''
            $normalized = $normalized -replace '^git@github\.com:',''
            $normalized = $normalized -replace '^https://github\.com/',''
            if ($normalized -ne $ExpectedRemoteSlug) {
                throw "Remote mismatch. Expected '$ExpectedRemoteSlug' but found '$normalized'."
            }
        }
    }

    Assert-NoSensitivePaths

    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $branch = "$BranchPrefix-$timestamp"
    Invoke-Git switch -c $branch | Out-Null
    Invoke-Git add -A | Out-Null
    Assert-NoSensitivePaths

    $staged = @(Invoke-Git diff --cached --name-only)
    if ($staged.Count -gt 0 -and -not ([string]::IsNullOrWhiteSpace(($staged -join '')))) {
        $hasName = (& git config user.name 2>$null); $nameExit = $LASTEXITCODE
        $hasEmail = (& git config user.email 2>$null); $emailExit = $LASTEXITCODE
        if ($nameExit -ne 0 -or [string]::IsNullOrWhiteSpace(($hasName | Out-String))) {
            Invoke-Git config user.name "Pseudo Codex Bootstrap" | Out-Null
        }
        if ($emailExit -ne 0 -or [string]::IsNullOrWhiteSpace(($hasEmail | Out-String))) {
            Invoke-Git config user.email "pseudo-codex-bootstrap@users.noreply.github.com" | Out-Null
        }
        Invoke-Git commit -m "chore: bootstrap current local state for pseudo-codex" | Out-Null
    }

    Invoke-Git push -u $Remote $branch | Out-Null
    $head = (Invoke-Git rev-parse HEAD | Select-Object -First 1).Trim()

    Write-Output "PSEUDO_CODEX_BOOTSTRAP_OK"
    Write-Output "branch=$branch"
    Write-Output "head=$head"
    Write-Output "remote=$remoteUrl"
}
finally {
    Pop-Location
}
