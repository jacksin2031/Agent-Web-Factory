[CmdletBinding()]
param(
    [ValidateSet('All', 'Universal', 'Codex', 'Gemini', 'Copilot', 'Claude')]
    [string]$Runtime = 'All',

    [ValidateSet('User', 'Project')]
    [string]$Scope = 'User',

    [string]$ProjectPath = (Get-Location).Path,
    [string]$Repository = 'jacksin2031/Agent-Web-Factory',
    [string]$Ref = 'main',
    [switch]$KeepBackup
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$SkillName = 'agent-web-factory'
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("agent-web-factory-install-" + [Guid]::NewGuid().ToString('N'))
$ZipPath = Join-Path $TempRoot 'source.zip'
$ExtractPath = Join-Path $TempRoot 'source'

function Write-Step([string]$Message) {
    Write-Host "[Agent Web Factory] $Message"
}

function Get-HomeDirectory {
    if ($HOME) { return $HOME }
    return [Environment]::GetFolderPath('UserProfile')
}

function Get-InstallTargets {
    param(
        [string]$RequestedRuntime,
        [string]$RequestedScope,
        [string]$RequestedProjectPath
    )

    $targets = New-Object System.Collections.Generic.List[string]
    $homeDir = Get-HomeDirectory

    if ($RequestedScope -eq 'User') {
        $universal = Join-Path $homeDir ".agents\skills\$SkillName"
        $claude = Join-Path $homeDir ".claude\skills\$SkillName"
    }
    else {
        $projectRoot = [System.IO.Path]::GetFullPath($RequestedProjectPath)
        $universal = Join-Path $projectRoot ".agents\skills\$SkillName"
        $claude = Join-Path $projectRoot ".claude\skills\$SkillName"
    }

    switch ($RequestedRuntime) {
        'All' {
            $targets.Add($universal)
            $targets.Add($claude)
        }
        'Universal' { $targets.Add($universal) }
        'Codex' { $targets.Add($universal) }
        'Gemini' { $targets.Add($universal) }
        'Copilot' { $targets.Add($universal) }
        'Claude' { $targets.Add($claude) }
    }

    return $targets | Select-Object -Unique
}

function Install-SkillCopy {
    param(
        [string]$SourcePath,
        [string]$TargetPath,
        [bool]$PreserveBackup
    )

    $parent = Split-Path -Parent $TargetPath
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    $stage = "$TargetPath.installing-$([Guid]::NewGuid().ToString('N'))"
    $backup = "$TargetPath.backup-$(Get-Date -Format 'yyyyMMddHHmmss')"

    try {
        New-Item -ItemType Directory -Force -Path $stage | Out-Null
        Get-ChildItem -LiteralPath $SourcePath -Force | Copy-Item -Destination $stage -Recurse -Force

        $installedSkill = Join-Path $stage 'SKILL.md'
        if (-not (Test-Path -LiteralPath $installedSkill -PathType Leaf)) {
            throw "The staged installation does not contain SKILL.md."
        }

        if (Test-Path -LiteralPath $TargetPath) {
            Move-Item -LiteralPath $TargetPath -Destination $backup
        }

        Move-Item -LiteralPath $stage -Destination $TargetPath

        if ((Test-Path -LiteralPath $backup) -and -not $PreserveBackup) {
            Remove-Item -LiteralPath $backup -Recurse -Force
        }
    }
    catch {
        if (Test-Path -LiteralPath $stage) {
            Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
        }
        if ((Test-Path -LiteralPath $backup) -and -not (Test-Path -LiteralPath $TargetPath)) {
            Move-Item -LiteralPath $backup -Destination $TargetPath -ErrorAction SilentlyContinue
        }
        throw
    }
}

try {
    Write-Step "Preparing installation."
    New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
    New-Item -ItemType Directory -Force -Path $ExtractPath | Out-Null

    $archiveUrl = "https://github.com/$Repository/archive/refs/heads/$Ref.zip"
    Write-Step "Downloading $Repository ($Ref)."
    Invoke-WebRequest -Uri $archiveUrl -OutFile $ZipPath -UseBasicParsing

    Expand-Archive -LiteralPath $ZipPath -DestinationPath $ExtractPath -Force

    $sourceRoot = Get-ChildItem -LiteralPath $ExtractPath -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') } |
        Select-Object -First 1

    if (-not $sourceRoot) {
        throw "Downloaded repository does not contain a root SKILL.md."
    }

    $skillText = Get-Content -LiteralPath (Join-Path $sourceRoot.FullName 'SKILL.md') -Raw
    if ($skillText -notmatch '(?m)^name:\s*agent-web-factory\s*$') {
        throw "SKILL.md identity check failed. Expected name: agent-web-factory."
    }

    $targets = @(Get-InstallTargets -RequestedRuntime $Runtime -RequestedScope $Scope -RequestedProjectPath $ProjectPath)
    if ($targets.Count -eq 0) {
        throw "No installation target was selected."
    }

    foreach ($target in $targets) {
        Write-Step "Installing to $target"
        Install-SkillCopy -SourcePath $sourceRoot.FullName -TargetPath $target -PreserveBackup $KeepBackup.IsPresent
    }

    Write-Host ''
    Write-Host 'Agent Web Factory installed successfully.' -ForegroundColor Green
    Write-Host 'Installed locations:'
    foreach ($target in $targets) {
        Write-Host "  - $target"
    }
    Write-Host ''
    Write-Host 'Restart or reload your AI coding agent if it was already running.'
    Write-Host 'Then ask it to use Agent Web Factory, or invoke agent-web-factory explicitly when supported.'
}
finally {
    if (Test-Path -LiteralPath $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
