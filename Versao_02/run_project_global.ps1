Write-Host "=== INICIANDO CONFIGURAÇÃO AUTOMÁTICA GLOBAL ===" -ForegroundColor Green

# Kill existing locking processes to release db.sqlite3 file locks
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
python manage.py makemigrations accounts companies audit

Write-Host "3. Executando as migrações de banco de dados (SQLite)..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "4. Populando o banco com dados iniciais (Seed)..." -ForegroundColor Yellow
python manage.py seed_initial_data

Write-Host "5. Executando testes automatizados do Módulo 1..." -ForegroundColor Yellow
python manage.py test apps.accounts.tests apps.companies.tests apps.audit.tests

Write-Host "6. Iniciando o servidor de desenvolvimento Django..." -ForegroundColor Green
python manage.py runserver
