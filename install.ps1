# ============================================================
#  Browser Harness MCP - Windows Installer (PowerShell)
#  Usage:
#    .\install.ps1
#    .\install.ps1 -InstallDir "D:\my-tools\browser-harness-mcp"
# ============================================================

param (
    [string]$InstallDir = "$env:USERPROFILE\browser-harness-mcp"
)

$REPO_URL  = "https://github.com/Arneld18/Browser-Harness-MCP"
$MCP_ENTRY = Join-Path $InstallDir "mcp_server.py"
$PYTHON    = Join-Path $InstallDir ".venv\Scripts\python.exe"

# ---------- Helpers -----------------------------------------

function Write-Step([string]$msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function Write-OK([string]$msg) {
    Write-Host "  [OK] $msg" -ForegroundColor Green
}

function Write-Warn([string]$msg) {
    Write-Host "  [!!] $msg" -ForegroundColor Yellow
}

function Require-Command([string]$cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "ERROR: '$cmd' is not installed or not in PATH." -ForegroundColor Red
        Write-Host "  Please install it and rerun this script." -ForegroundColor Red
        exit 1
    }
}

# ---------- 1. Check prerequisites --------------------------

Write-Step "Checking prerequisites..."
Require-Command "git"

$hasUv     = [bool](Get-Command "uv"     -ErrorAction SilentlyContinue)
$hasPython = [bool](Get-Command "python" -ErrorAction SilentlyContinue)

if (-not $hasUv -and -not $hasPython) {
    Write-Host ""
    Write-Host "ERROR: Neither 'uv' nor 'python' found in PATH." -ForegroundColor Red
    Write-Host "  Install uv (recommended): https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Red
    Write-Host "  Or install Python 3.11+:  https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Write-OK "git found"
if ($hasUv)      { Write-OK   "uv found (will be used for dependency install)" }
elseif ($hasPython) { Write-Warn "uv not found -- falling back to pip" }

# ---------- 2. Clone repository -----------------------------

Write-Step "Cloning repository..."

if (Test-Path $InstallDir) {
    Write-Warn "Directory already exists: $InstallDir"
    Write-Warn "Pulling latest changes instead of cloning..."
    Push-Location $InstallDir
    git pull --ff-only
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: git pull failed. Please resolve manually." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
} else {
    git clone $REPO_URL $InstallDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: git clone failed." -ForegroundColor Red
        exit 1
    }
}

Write-OK "Repository ready at: $InstallDir"

# ---------- 3. Install dependencies -------------------------

Write-Step "Installing dependencies..."
Push-Location $InstallDir

if ($hasUv) {
    uv sync
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: uv sync failed." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    $PYTHON = Join-Path $InstallDir ".venv\Scripts\python.exe"
} else {
    # pip fallback -- create venv manually then install
    python -m venv (Join-Path $InstallDir ".venv")
    $pipPython = Join-Path $InstallDir ".venv\Scripts\python.exe"
    & $pipPython -m pip install --quiet -e .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: pip install failed." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    $PYTHON = $pipPython
}

Pop-Location
Write-OK "Dependencies installed"

# ---------- 4. Build mcp.json block -------------------------

# Escape backslashes for JSON
$jsonPython = $PYTHON.Replace("\", "\\")
$jsonEntry  = $MCP_ENTRY.Replace("\", "\\")

$mcpBlock = @"
{
  "mcpServers": {
    "browser-harness": {
      "command": "$jsonPython",
      "args": [
        "$jsonEntry"
      ],
      "env": {}
    }
  }
}
"@

# ---------- 5. Print result ---------------------------------

$border  = "=" * 56
$divider = "-" * 56

Write-Host ""
Write-Host $border -ForegroundColor Green
Write-Host "  [OK]  Browser Harness MCP installed successfully!" -ForegroundColor Green
Write-Host $border -ForegroundColor Green
Write-Host ""
Write-Host "  Install path : $InstallDir" -ForegroundColor White
Write-Host "  Python       : $PYTHON" -ForegroundColor White
Write-Host ""
Write-Host $divider
Write-Host "  STEP 1 -- Add this block to your mcp.json" -ForegroundColor Yellow
Write-Host $divider
Write-Host ""
Write-Host $mcpBlock -ForegroundColor White
Write-Host ""
Write-Host $divider
Write-Host "  STEP 2 -- Common mcp.json locations" -ForegroundColor Yellow
Write-Host $divider
Write-Host ""
Write-Host "  Antigravity    : Check your Antigravity MCP settings panel" -ForegroundColor White
Write-Host "  Claude Desktop : $env:APPDATA\Claude\claude_desktop_config.json" -ForegroundColor Gray
Write-Host ""
Write-Host $divider
Write-Host "  STEP 3 -- Restart your AI agent" -ForegroundColor Yellow
Write-Host $divider
Write-Host ""
Write-Host "  Restart Antigravity / Claude Desktop after saving mcp.json." -ForegroundColor White
Write-Host "  Chrome will launch automatically on the first browser tool call." -ForegroundColor White
Write-Host ""
Write-Host "  Need help? Read: $InstallDir\install.md" -ForegroundColor Gray
Write-Host $border -ForegroundColor Green
Write-Host ""
