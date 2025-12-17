# Script PowerShell equivalent au Makefile
# Utiliser: .\make.ps1 <commande>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Commandes disponibles:" -ForegroundColor Cyan
    Write-Host "  .\make.ps1 test       - Lancer tous les tests" -ForegroundColor Green
    Write-Host "  .\make.ps1 unit_test  - Lancer tests unitaires + integration" -ForegroundColor Green
    Write-Host "  .\make.ps1 perf_test  - Lancer tests de performance" -ForegroundColor Green
    Write-Host "  .\make.ps1 coverage   - Generer rapport de couverture" -ForegroundColor Green
    Write-Host "  .\make.ps1 lint       - Verifier qualite du code" -ForegroundColor Green
    Write-Host "  .\make.ps1 doc        - Generer documentation HTML" -ForegroundColor Green
    Write-Host "  .\make.ps1 clean      - Nettoyer fichiers generes" -ForegroundColor Green
}

function Run-Test {
    Write-Host "Lancement de tous les tests..." -ForegroundColor Yellow
    pytest tests/ -v
}

function Run-UnitTest {
    Write-Host "Lancement des tests unitaires et integration..." -ForegroundColor Yellow
    pytest tests/unit/ tests/integration/ -v
}

function Run-PerfTest {
    Write-Host "Lancement des tests de performance..." -ForegroundColor Yellow
    pytest tests/performance/ -v -m performance
}

function Run-Coverage {
    Write-Host "Generation du rapport de couverture..." -ForegroundColor Yellow
    coverage run -m pytest tests/unit/ tests/integration/
    coverage report
    coverage html
    Write-Host "Rapport HTML genere dans htmlcov/index.html" -ForegroundColor Green
}

function Run-Lint {
    Write-Host "Verification de la qualite du code..." -ForegroundColor Yellow
    ruff check .
}

function Run-Doc {
    Write-Host "Generation de la documentation..." -ForegroundColor Yellow
    pdoc --html --output-dir docs --force triangulator_core app
    Write-Host "Documentation generee dans docs/" -ForegroundColor Green
}

function Run-Clean {
    Write-Host "Nettoyage des fichiers generes..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__, .pytest_cache, .coverage, htmlcov, docs
    Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
    Write-Host "Nettoyage termine!" -ForegroundColor Green
}

# Execution de la commande
switch ($Command.ToLower()) {
    "test" { Run-Test }
    "unit_test" { Run-UnitTest }
    "perf_test" { Run-PerfTest }
    "coverage" { Run-Coverage }
    "lint" { Run-Lint }
    "doc" { Run-Doc }
    "clean" { Run-Clean }
    "help" { Show-Help }
    default {
        Write-Host "Commande inconnue: $Command" -ForegroundColor Red
        Show-Help
    }
}
