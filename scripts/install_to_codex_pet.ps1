param(
    [string]$PackageDir,
    [string]$CodexHome,
    [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[corgi-pet] $Message" -ForegroundColor Cyan
}

function Ensure-PathWithin {
    param(
        [string]$BasePath,
        [string]$TargetPath
    )

    $baseResolved = [System.IO.Path]::GetFullPath($BasePath)
    $targetResolved = [System.IO.Path]::GetFullPath($TargetPath)

    if (-not $targetResolved.StartsWith($baseResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to modify path outside base directory. Base: $baseResolved Target: $targetResolved"
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not $PackageDir) {
    $PackageDir = Join-Path $repoRoot "build\\package"
}

if (-not $CodexHome) {
    if ($env:CODEX_HOME) {
        $CodexHome = $env:CODEX_HOME
    } else {
        $CodexHome = Join-Path $HOME ".codex"
    }
}

$packageDirResolved = [System.IO.Path]::GetFullPath($PackageDir)
$codexHomeResolved = [System.IO.Path]::GetFullPath($CodexHome)
$petJsonPath = Join-Path $packageDirResolved "pet.json"
$spritesheetPath = Join-Path $packageDirResolved "spritesheet.webp"

if (-not (Test-Path $petJsonPath)) {
    throw "Missing pet.json in package directory: $petJsonPath`nPlease run: python scripts/build_pet_package.py"
}

if (-not (Test-Path $spritesheetPath)) {
    throw "Missing spritesheet.webp in package directory: $spritesheetPath`nPlease run: python scripts/build_pet_package.py"
}

$petMeta = Get-Content -Raw -Encoding UTF8 $petJsonPath | ConvertFrom-Json

if (-not $petMeta.id) {
    throw "pet.json is missing a pet id."
}

$petsRoot = Join-Path $codexHomeResolved "pets"
$targetDir = Join-Path $petsRoot $petMeta.id
$backupRoot = Join-Path $codexHomeResolved "pets-backups"

Write-Step "Package directory: $packageDirResolved"
Write-Step "Codex home: $codexHomeResolved"
Write-Step "Target pet id: $($petMeta.id)"

New-Item -ItemType Directory -Force -Path $petsRoot | Out-Null

Ensure-PathWithin -BasePath $codexHomeResolved -TargetPath $targetDir
Ensure-PathWithin -BasePath $codexHomeResolved -TargetPath $backupRoot

if ((Test-Path $targetDir) -and (-not $SkipBackup)) {
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupDir = Join-Path $backupRoot "$($petMeta.id)-$timestamp"
    Write-Step "Backing up existing install to: $backupDir"
    Copy-Item -Recurse -Force -Path $targetDir -Destination $backupDir
}

if (Test-Path $targetDir) {
    Write-Step "Removing previous install"
    Remove-Item -LiteralPath $targetDir -Recurse -Force
}

Write-Step "Copying new pet package"
Copy-Item -Recurse -Force -Path $packageDirResolved -Destination $targetDir

$installedPetJson = Join-Path $targetDir "pet.json"
$installedSheet = Join-Path $targetDir "spritesheet.webp"

if (-not (Test-Path $installedPetJson) -or -not (Test-Path $installedSheet)) {
    throw "Install completed but expected files were not found in $targetDir"
}

Write-Host ""
Write-Host "Install complete." -ForegroundColor Green
Write-Host "Pet name: $($petMeta.displayName)"
Write-Host "Installed to: $targetDir"
Write-Host "Restart or refresh Codex if the pet is already open."
