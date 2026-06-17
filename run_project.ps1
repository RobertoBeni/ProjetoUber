Write-Host "=== INICIANDO CONFIGURAÇÃO AUTOMÁTICA DO PROJETO ===" -ForegroundColor Green

Write-Host "1. Criando o Ambiente Virtual (venv)..." -ForegroundColor Yellow
python -m venv venv

Write-Host "2. Instalando as dependências do requirements.txt..." -ForegroundColor Yellow
.\venv\Scripts\pip install -r requirements.txt

Write-Host "3. Gerando arquivos de migração para os apps customizados..." -ForegroundColor Yellow
.\venv\Scripts\python manage.py makemigrations accounts companies audit

Write-Host "4. Executando as migrações de banco de dados (SQLite)..." -ForegroundColor Yellow
.\venv\Scripts\python manage.py migrate

Write-Host "5. Populando o banco com dados iniciais (Seed)..." -ForegroundColor Yellow
.\venv\Scripts\python manage.py seed_initial_data

Write-Host "6. Executando testes automatizados do Módulo 1..." -ForegroundColor Yellow
.\venv\Scripts\python manage.py test apps.accounts.tests apps.companies.tests apps.audit.tests

Write-Host "7. Iniciando o servidor de desenvolvimento Django..." -ForegroundColor Green
.\venv\Scripts\python manage.py runserver
