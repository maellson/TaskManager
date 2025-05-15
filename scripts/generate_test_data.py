# scripts/generate_test_data.py
from core.tests.factories import (
    create_test_users, create_test_resources, create_test_process,
    create_approval_levels, create_test_tasks, create_concurrency_rules
)
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importar funções de teste


def main():
    print("Criando dados de teste...")

    users = create_test_users()
    resources = create_test_resources()
    process = create_test_process(users['project_manager'], resources)
    approval_levels = create_approval_levels(users, process)
    tasks = create_test_tasks(process, users, resources)
    rules = create_concurrency_rules(process)

    print("Dados de teste criados com sucesso!")


if __name__ == "__main__":
    main()
