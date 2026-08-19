$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = Join-Path ([System.IO.Path]::GetTempPath()) ("pseudo-codex-bootstrap-test-" + [guid]::NewGuid().ToString('N'))
$remote = Join-Path $root 'remote.git'
$work = Join-Path $root 'work'
$secretWork = Join-Path $root 'secret-work'
$tokenWork = Join-Path $root 'token-work'
$scriptPath = Join-Path $PSScriptRoot 'Bootstrap-LocalRepo.ps1'

function GitAt {
    param(
        [Parameter(Position = 0, Mandatory = $true)][string]$Path,
        [Parameter(Position = 1, ValueFromRemainingArguments = $true)][string[]]$GitArgs
    )
    $out = & git -C $Path @GitArgs 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git failed: $($out -join [Environment]::NewLine)" }
    return @($out)
}

try {
    New-Item -ItemType Directory -Path $root | Out-Null
    & git init --bare $remote | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'could not init bare remote' }

    New-Item -ItemType Directory -Path $work | Out-Null
    & git init -b main $work | Out-Null
    GitAt $work config user.name 'Test User' | Out-Null
    GitAt $work config user.email 'test@example.invalid' | Out-Null
    Set-Content -LiteralPath (Join-Path $work 'app.txt') -Value 'old' -NoNewline
    GitAt $work add app.txt | Out-Null
    GitAt $work commit -m 'initial' | Out-Null
    GitAt $work remote add origin $remote | Out-Null
    GitAt $work push -u origin main | Out-Null

    Set-Content -LiteralPath (Join-Path $work 'app.txt') -Value 'new' -NoNewline
    Set-Content -LiteralPath (Join-Path $work 'new-file.txt') -Value 'included' -NoNewline

    $result = @(& $scriptPath -LocalPath $work -Remote origin -BranchPrefix 'pseudo-codex-test' -TestMode)
    if ($LASTEXITCODE -ne 0) { throw 'bootstrap script returned a non-zero exit code' }
    if (-not ($result -contains 'PSEUDO_CODEX_BOOTSTRAP_OK')) { throw 'success marker missing' }
    $branchLine = $result | Where-Object { $_ -like 'branch=*' } | Select-Object -First 1
    if (-not $branchLine) { throw 'branch marker missing' }
    $branch = $branchLine.Substring('branch='.Length)

    $remoteContent = (& git --git-dir=$remote show "${branch}:app.txt") -join "`n"
    if ($LASTEXITCODE -ne 0 -or $remoteContent -ne 'new') { throw 'latest local content was not pushed' }
    $newFileContent = (& git --git-dir=$remote show "${branch}:new-file.txt") -join "`n"
    if ($LASTEXITCODE -ne 0 -or $newFileContent -ne 'included') { throw 'new local file was not pushed' }

    & git clone $remote $secretWork | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'could not clone secret guard fixture' }
    GitAt $secretWork switch main | Out-Null
    Set-Content -LiteralPath (Join-Path $secretWork '.env') -Value 'SECRET=do-not-push' -NoNewline

    $pathGuardBlocked = $false
    try {
        & $scriptPath -LocalPath $secretWork -Remote origin -BranchPrefix 'pseudo-codex-secret-test' -TestMode | Out-Null
    }
    catch {
        if ($_.Exception.Message -match 'Sensitive-looking files detected') { $pathGuardBlocked = $true }
        else { throw }
    }
    if (-not $pathGuardBlocked) { throw 'sensitive file guard did not block .env' }

    & git clone $remote $tokenWork | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'could not clone token guard fixture' }
    GitAt $tokenWork switch main | Out-Null
    Set-Content -LiteralPath (Join-Path $tokenWork 'config.txt') -Value 'API_KEY=sk-abcdefghijklmnopqrstuvwxyz1234567890' -NoNewline

    $contentGuardBlocked = $false
    try {
        & $scriptPath -LocalPath $tokenWork -Remote origin -BranchPrefix 'pseudo-codex-token-test' -TestMode | Out-Null
    }
    catch {
        if ($_.Exception.Message -match 'Sensitive-looking content detected') { $contentGuardBlocked = $true }
        else { throw }
    }
    if (-not $contentGuardBlocked) { throw 'sensitive content guard did not block token-like content' }

    Write-Output 'WINDOWS_BOOTSTRAP_TEST_OK'
}
finally {
    if (Test-Path $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
