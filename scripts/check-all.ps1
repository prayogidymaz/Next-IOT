# Next-IoT — unified engineering guardrails check (Step 0+)
$Root = Split-Path -Parent $PSScriptRoot
$Compose = "$Root/docker-compose.yml"

function Invoke-CheckStep {
    param(
        [string]$Label,
        [scriptblock]$Action
    )
    Write-Host "==> $Label" -ForegroundColor Cyan
    & $Action
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Host "[FAIL] $Label" -ForegroundColor Red
        exit 1
    }
}

Invoke-CheckStep "API ruff" {
    docker compose -f $Compose exec -T api ruff check app tests
}

Invoke-CheckStep "API mypy" {
    docker compose -f $Compose exec -T api mypy app
}

Invoke-CheckStep "RATCHET legacy budget" {
    python "$Root/scripts/count_ratchet_entries.py"
}

Invoke-CheckStep "API pytest" {
    docker compose -f $Compose exec -T api pytest -q
}

Invoke-CheckStep "Web lint" {
    Push-Location "$Root/apps/web"
    npm run lint
    Pop-Location
}

Invoke-CheckStep "Web typecheck" {
    Push-Location "$Root/apps/web"
    npm run typecheck
    Pop-Location
}

Invoke-CheckStep "Flutter analyze (field_app)" {
    Push-Location "$Root/apps/mobile/field_app"
    flutter analyze
    Pop-Location
}

Invoke-CheckStep "Forbidden pattern scan" {
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
    $apiHits = Select-String -CaseSensitive -Path (Get-ChildItem -Path "$Root/apps/api/app" -Recurse -Include *.py).FullName -Pattern 'type: ignore|from typing import[^\n]*\bAny\b|\btyping\.Any\b|: Any\b|\[Any\]' -ErrorAction SilentlyContinue
    $dartHits = Select-String -Path (Get-ChildItem -Path "$Root/apps/mobile/field_app/lib" -Recurse -Include *.dart).FullName -Pattern '\bdynamic\b' -ErrorAction SilentlyContinue

    if ($webHits.Count -gt 0 -or $apiHits.Count -gt 0 -or $dartHits.Count -gt 0) {
        Write-Host "Forbidden patterns found:" -ForegroundColor Red
        $webHits | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
        $apiHits | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
        $dartHits | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
        exit 1
    }
}

Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
