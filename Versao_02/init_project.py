import os

def create_file(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {path}")

def scaffold_project():
    workspace = r"e:\ProjetoUber"
    
    # 1. Apps list
    apps = [
        "core", "accounts", "companies", "drivers", "vehicles", 
        "cargo", "freight", "pricing", "matching", "routing", 
        "tracking", "eta", "payments", "documents", "notifications", 
        "support", "ai_assistant", "audit"
    ]
    
    # Create app structures
    for app in apps:
        app_dir = os.path.join(workspace, "apps", app)
        os.makedirs(app_dir, exist_ok=True)
        
        # Files for each app
        create_file(os.path.join(app_dir, "__init__.py"))
        create_file(os.path.join(app_dir, "models.py"), "from django.db import models\n")
        create_file(os.path.join(app_dir, "serializers.py"), "from rest_framework import serializers\n")
        create_file(os.path.join(app_dir, "views.py"), "from rest_framework import viewsets\n")
        create_file(os.path.join(app_dir, "urls.py"), "from django.urls import path\n\nurlpatterns = []\n")
        create_file(os.path.join(app_dir, "services.py"), f"# Services for {app}\n")
        create_file(os.path.join(app_dir, "permissions.py"), "from rest_framework import permissions\n")
        create_file(os.path.join(app_dir, "admin.py"), "from django.contrib import admin\n")
        create_file(os.path.join(app_dir, "tests.py"), "from django.test import TestCase\n")

    # 2. Config & Settings structures
    config_dir = os.path.join(workspace, "config")
    settings_dir = os.path.join(config_dir, "settings")
    os.makedirs(settings_dir, exist_ok=True)
    
    create_file(os.path.join(config_dir, "__init__.py"))
    create_file(os.path.join(settings_dir, "__init__.py"))
    create_file(os.path.join(settings_dir, "base.py"), "# Base Django Settings\n")
    create_file(os.path.join(settings_dir, "development.py"), "from .base import *\n")
    create_file(os.path.join(settings_dir, "production.py"), "from .base import *\n")

    print("Project scaffolding complete.")

if __name__ == "__main__":
    scaffold_project()
