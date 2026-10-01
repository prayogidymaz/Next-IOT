# Next-IoT — unified engineering guardrails check (Step 0+)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

function Fail($msg) {
  Write-Host "CHECK FAILED: $msg" -ForegroundColor Red
  exit 1
}

Write-Host "==> [1/6] API ruff" -ForegroundColor Cyan
docker compose -f "$Root/docker-compose.yml" exec -T api ruff check . 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { docker compose -f "$Root/docker-compose.yml" exec -T api ruff check .; Fail "ruff" }

Write-Host "==> [2/6] API mypy" -ForegroundColor Cyan
docker compose -f "$Root/docker-compose.yml" exec -T api mypy . 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { docker compose -f "$Root/docker-compose.yml" exec -T api mypy .; Fail "mypy" }

Write-Host "==> [3/6] API pytest" -ForegroundColor Cyan
docker compose -f "$Root/docker-compose.yml" exec -T api pytest -q 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { docker compose -f "$Root/docker-compose.yml" exec -T api pytest -q; Fail "pytest" }

Write-Host "==> [4/6] Web lint + typecheck" -ForegroundColor Cyan
Push-Location "$Root/apps/web"
npm run lint 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { npm run lint; Pop-Location; Fail "web lint" }
npm run typecheck 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { npm run typecheck; Pop-Location; Fail "web typecheck" }
Pop-Location

Write-Host "==> [5/6] Flutter analyze (field_app)" -ForegroundColor Cyan
Push-Location "$Root/apps/mobile/field_app"
flutter analyze 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { flutter analyze; Pop-Location; Fail "flutter analyze" }
Pop-Location

Write-Host "==> [6/6] Forbidden pattern scan" -ForegroundColor Cyan
$webPaths = @(
  "$Root/apps/web/app",
  "$Root/apps/web/components",
  "$Root/apps/web/hooks",
  "$Root/apps/web/lib"
)
$webHits = @()
foreach ($p in $webPaths) {
  if (Test-Path $p) {
    $webHits += Select-String -Path (Get-ChildItem -Path $p -Recurse -Include *.ts,*.tsx).FullName -Pattern ': any\b|as any\b|as unknown as|@ts-ignore|@ts-expect-error' -ErrorAction SilentlyContinue
  }
}
$apiHits = Select-String -Path (Get-ChildItem -Path "$Root/apps/api/app" -Recurse -Include *.py).FullName -Pattern 'type: ignore|from typing import[^\n]*\bAny\b|\btyping\.Any\b|: Any\b|\[Any\]' -ErrorAction SilentlyContinue
$dartHits = Select-String -Path (Get-ChildItem -Path "$Root/apps/mobile/field_app/lib" -Recurse -Include *.dart).FullName -Pattern '\bdynamic\b' -ErrorAction SilentlyContinue

if ($webHits.Count -gt 0 -or $apiHits.Count -gt 0 -or $dartHits.Count -gt 0) {
  Write-Host "Forbidden patterns found:" -ForegroundColor Red
  $webHits | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
  $apiHits | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
  $dartHits | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
  Fail "forbidden patterns"
}

Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
