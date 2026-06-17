Write-Host "=== INICIANDO CONFIGURAÇÃO AUTOMÁTICA GLOBAL ===" -ForegroundColor Green

# Kill the exact process listening on port 8000 to unlock db.sqlite3
Write-Host "Verificando se há processos ocupando a porta 8000..." -ForegroundColor Yellow
$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    Write-Host "Terminando o processo ocupando a porta 8000 (PID: $($conn.OwningProcess))..." -ForegroundColor Yellow
    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Kill any stray generic python/daphne processes
Write-Host "Limpando processos Python e Daphne ativos..." -ForegroundColor Yellow
Stop-Process -Name python -ErrorAction SilentlyContinue -Force
Stop-Process -Name daphne -ErrorAction SilentlyContinue -Force
Start-Sleep -Seconds 2

# Self-healing clean database check to prevent InconsistentMigrationHistory errors
if (Test-Path db.sqlite3) {
    Write-Host "Limpando histórico antigo de banco de dados (db.sqlite3)..." -ForegroundColor Yellow
    Remove-Item db.sqlite3 -Force
}

Write-Host "1. Instalando dependências globalmente..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

Write-Host "2. Gerando arquivos de migração para os apps..." -ForegroundColor Yellow
python manage.py makemigrations accounts companies audit drivers vehicles cargo documents

Write-Host "3. Executando as migrações de banco de dados (SQLite)..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "4. Populando o banco com dados iniciais e métricas de demonstração (Seed)..." -ForegroundColor Yellow
python manage.py seed_initial_data
python manage.py seed_demo_dashboard

Write-Host "5. Executando todos os testes automatizados (Módulo 1 e Módulo 2)..." -ForegroundColor Yellow
python manage.py test apps.accounts.tests apps.companies.tests apps.audit.tests apps.drivers.tests apps.vehicles.tests apps.cargo.tests apps.documents.tests apps.tracking.tests apps.support.tests apps.freight.tests apps.core.tests apps.commercial.tests apps.ai_assistant.tests

Write-Host "6. Iniciando o servidor de desenvolvimento Django..." -ForegroundColor Green
python manage.py runserver
