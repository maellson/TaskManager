# Coloque este script em um arquivo como test_script.py
# Execute com: python manage.py shell < test_script.py

from core.models import ApprovalLevel, ApprovalAuthority
from core.services.process_service import apply_change_request
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from core.models import (Process, Task, TaskDependency, ConcurrencyRule,
                         Resource, ProcessResource, TaskResource,
                         ApprovalLevel, ApprovalAuthority, ChangeRequest)
from core.services.task_service import can_tasks_run_concurrently
User = get_user_model()


# Limpar dados existentes (opcional)
# User.objects.all().delete()
# Process.objects.all().delete()
# Resource.objects.all().delete()
# ApprovalLevel.objects.all().delete()

# criando o usuarios no sistema
def create_test_users():
    # Gerente de Projeto
    project_manager = User.objects.create_user(
        username='pm_user',
        email='pm@example.com',
        password='pm_password',
        first_name='Gerente',
        last_name='Projeto',
        user_type='project_manager'
    )

    # Usuários regulares (responsáveis por tarefas)
    engineer = User.objects.create_user(
        username='engineer',
        email='engineer@example.com',
        password='engineer_password',
        first_name='Engenheiro',
        last_name='Civil',
        user_type='regular'
    )

    plumber = User.objects.create_user(
        username='plumber',
        email='plumber@example.com',
        password='plumber_password',
        first_name='Encanador',
        last_name='Silva',
        user_type='regular'
    )

    electrician = User.objects.create_user(
        username='electrician',
        email='electrician@example.com',
        password='electrician_password',
        first_name='Eletricista',
        last_name='Santos',
        user_type='regular'
    )

    painter = User.objects.create_user(
        username='painter',
        email='painter@example.com',
        password='painter_password',
        first_name='Pintor',
        last_name='Pereira',
        user_type='regular'
    )

    # Aprovadores
    approver1 = User.objects.create_user(
        username='approver1',
        email='approver1@example.com',
        password='approver1_password',
        first_name='Aprovador',
        last_name='Nível 1',
        user_type='regular'
    )

    approver2 = User.objects.create_user(
        username='approver2',
        email='approver2@example.com',
        password='approver2_password',
        first_name='Aprovador',
        last_name='Nível 2',
        user_type='regular'
    )

    return {
        'project_manager': project_manager,
        'engineer': engineer,
        'plumber': plumber,
        'electrician': electrician,
        'painter': painter,
        'approver1': approver1,
        'approver2': approver2
    }


# 2. criando recursos
def create_test_resources():
    # Materiais
    cement = Resource.objects.create(
        name='Cimento',
        resource_type='material',
        description='Saco de cimento 50kg',
        quantity_available=100,
        unit='saco'
    )

    sand = Resource.objects.create(
        name='Areia',
        resource_type='material',
        description='Areia fina para construção',
        quantity_available=5000,
        unit='kg'
    )

    paint = Resource.objects.create(
        name='Tinta',
        resource_type='material',
        description='Tinta acrílica premium',
        quantity_available=50,
        unit='galão'
    )

    # Equipamentos
    concrete_mixer = Resource.objects.create(
        name='Betoneira',
        resource_type='equipment',
        description='Betoneira 400L',
        quantity_available=3,
        unit='un'
    )

    ladder = Resource.objects.create(
        name='Escada',
        resource_type='equipment',
        description='Escada extensível 6m',
        quantity_available=5,
        unit='un'
    )

    return {
        'cement': cement,
        'sand': sand,
        'paint': paint,
        'concrete_mixer': concrete_mixer,
        'ladder': ladder
    }

# 3. criando processos com recursos associados


def create_test_process(project_manager, resources):
    # Criar processo
    house_construction = Process.objects.create(
        name='Construção de Casa Residencial',
        description='Projeto para construção de uma casa de 3 quartos',
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timezone.timedelta(days=180),
        is_active=True,
        created_by=project_manager,
        updated_by=project_manager
    )

    # Alocar recursos ao processo
    ProcessResource.objects.create(
        process=house_construction,
        resource=resources['cement'],
        quantity_allocated=Decimal('80')
    )

    ProcessResource.objects.create(
        process=house_construction,
        resource=resources['sand'],
        quantity_allocated=Decimal('4000')
    )

    ProcessResource.objects.create(
        process=house_construction,
        resource=resources['paint'],
        quantity_allocated=Decimal('30')
    )

    ProcessResource.objects.create(
        process=house_construction,
        resource=resources['concrete_mixer'],
        quantity_allocated=Decimal('2')
    )

    ProcessResource.objects.create(
        process=house_construction,
        resource=resources['ladder'],
        quantity_allocated=Decimal('3')
    )

    return house_construction


# 4. criando níveis de aprovação


def create_approval_levels(users, process):
    # Criar níveis de aprovação
    level1 = ApprovalLevel.objects.create(
        name='Aprovação Técnica',
        level=1,
        description='Aprovação de aspectos técnicos',
        required_approvers=1
    )

    level2 = ApprovalLevel.objects.create(
        name='Aprovação Gerencial',
        level=5,
        description='Aprovação de gerentes de projeto',
        required_approvers=1
    )

    # Criar autoridades de aprovação
    auth1 = ApprovalAuthority.objects.create(
        user=users['approver1'],
        level=level1
    )
    auth1.processes.add(process)

    auth2 = ApprovalAuthority.objects.create(
        user=users['project_manager'],
        level=level2
    )
    auth2.processes.add(process)

    return {
        'level1': level1,
        'level2': level2
    }


# 5. criando tarefas com atributos

def create_test_tasks(process, users, resources):
    # Tarefa 1: Fundação
    foundation = Task.objects.create(
        process=process,
        name='Preparar Fundação',
        description='Escavação e preparação da fundação',
        responsible=users['engineer'],
        planned_start_date=timezone.now(),
        planned_end_date=timezone.now() + timezone.timedelta(days=15),
        status='not_started',
        is_active=True,
        order=10,
        task_type='foundation',
        location='Terreno Completo'
    )

    # Recursos para Fundação
    TaskResource.objects.create(
        task=foundation,
        resource=resources['cement'],
        quantity_allocated=Decimal('30')
    )

    TaskResource.objects.create(
        task=foundation,
        resource=resources['sand'],
        quantity_allocated=Decimal('2000')
    )

    TaskResource.objects.create(
        task=foundation,
        resource=resources['concrete_mixer'],
        quantity_allocated=Decimal('1')
    )

    # Tarefa 2: Estrutura
    structure = Task.objects.create(
        process=process,
        name='Construir Estrutura',
        description='Construção das paredes e estrutura principal',
        responsible=users['engineer'],
        planned_start_date=timezone.now() + timezone.timedelta(days=16),
        planned_end_date=timezone.now() + timezone.timedelta(days=45),
        status='not_started',
        is_active=True,
        order=20,
        task_type='structure',
        location='Terreno Completo'
    )

    # Recursos para Estrutura
    TaskResource.objects.create(
        task=structure,
        resource=resources['cement'],
        quantity_allocated=Decimal('50')
    )

    TaskResource.objects.create(
        task=structure,
        resource=resources['sand'],
        quantity_allocated=Decimal('2000')
    )

    # Tarefa 3: Encanamento
    plumbing = Task.objects.create(
        process=process,
        name='Instalar Encanamento',
        description='Instalação do sistema hidráulico',
        responsible=users['plumber'],
        planned_start_date=timezone.now() + timezone.timedelta(days=46),
        planned_end_date=timezone.now() + timezone.timedelta(days=60),
        status='not_started',
        is_active=True,
        order=30,
        task_type='plumbing',
        location='Interior da Casa'
    )

    # Tarefa 4: Elétrica
    electrical = Task.objects.create(
        process=process,
        name='Instalar Sistema Elétrico',
        description='Instalação da fiação e componentes elétricos',
        responsible=users['electrician'],
        planned_start_date=timezone.now() + timezone.timedelta(days=46),
        planned_end_date=timezone.now() + timezone.timedelta(days=60),
        status='not_started',
        is_active=True,
        order=40,
        task_type='electrical',
        location='Interior da Casa'
    )

    # Tarefa 5: Pintura
    painting = Task.objects.create(
        process=process,
        name='Pintar Paredes',
        description='Pintura de paredes internas e externas',
        responsible=users['painter'],
        planned_start_date=timezone.now() + timezone.timedelta(days=61),
        planned_end_date=timezone.now() + timezone.timedelta(days=75),
        status='not_started',
        is_active=True,
        order=50,
        task_type='painting',
        location='Interior e Exterior da Casa'
    )

    # Recursos para Pintura
    TaskResource.objects.create(
        task=painting,
        resource=resources['paint'],
        quantity_allocated=Decimal('30')
    )

    TaskResource.objects.create(
        task=painting,
        resource=resources['ladder'],
        quantity_allocated=Decimal('2')
    )

    # Tarefa 6: Piso
    flooring = Task.objects.create(
        process=process,
        name='Instalar Piso',
        description='Instalação de piso cerâmico',
        responsible=users['engineer'],
        planned_start_date=timezone.now() + timezone.timedelta(days=61),
        planned_end_date=timezone.now() + timezone.timedelta(days=75),
        status='not_started',
        is_active=True,
        order=60,
        task_type='flooring',
        location='Interior da Casa'
    )

    # Estabelecer dependências entre tarefas
    # Estrutura depende de Fundação
    TaskDependency.objects.create(
        task=structure,
        prerequisite_task=foundation
    )

    # Encanamento depende de Estrutura
    TaskDependency.objects.create(
        task=plumbing,
        prerequisite_task=structure
    )

    # Elétrica depende de Estrutura
    TaskDependency.objects.create(
        task=electrical,
        prerequisite_task=structure
    )

    # Pintura depende de Encanamento e Elétrica
    TaskDependency.objects.create(
        task=painting,
        prerequisite_task=plumbing
    )

    TaskDependency.objects.create(
        task=painting,
        prerequisite_task=electrical
    )

    # Piso depende de Encanamento e Elétrica
    TaskDependency.objects.create(
        task=flooring,
        prerequisite_task=plumbing
    )

    TaskDependency.objects.create(
        task=flooring,
        prerequisite_task=electrical
    )

    return {
        'foundation': foundation,
        'structure': structure,
        'plumbing': plumbing,
        'electrical': electrical,
        'painting': painting,
        'flooring': flooring
    }


# Função para criar regras de concorrência

def create_concurrency_rules(process):
    # Regra: Mesmo responsável não pode executar tarefas concorrentes
    same_responsible_rule = ConcurrencyRule.objects.create(
        name='Mesmo Responsável',
        description='Tarefas com o mesmo responsável não podem ser executadas concorrentemente',
        rule_type='same_responsible',
        process=process,
        is_active=True
    )
    
    # Regra: Conflito de recursos (equipamentos)
    resource_conflict_rule = ConcurrencyRule.objects.create(
        name='Conflito de Equipamentos',
        description='Tarefas que usam os mesmos equipamentos não podem ser executadas concorrentemente',
        rule_type='resource_conflict',
        process=process,
        is_active=True
    )
    
    # Regra personalizada: Pintura e Piso no mesmo local
    custom_rule = ConcurrencyRule.objects.create(
        name='Pintura e Piso no Mesmo Local',
        description='Pintura e instalação de piso no mesmo local não podem ocorrer simultaneamente',
        rule_type='custom',
        process=process,
        custom_condition={
            'task_types': ['painting', 'flooring'],
            'same_location': True
        },
        is_active=True
    )
    
    return {
        'same_responsible_rule': same_responsible_rule,
        'resource_conflict_rule': resource_conflict_rule,
        'custom_rule': custom_rule
    }

# 1. Criar usuários
print("Criando usuários...")
users = create_test_users()

# 2. Criar recursos
print("Criando recursos...")
resources = create_test_resources()

# 3. Criar processo com recursos
print("Criando processo...")
process = create_test_process(users['project_manager'], resources)

# 4. Definir níveis de aprovação
print("Definindo níveis de aprovação...")
approval_levels = create_approval_levels(users, process)

# 5. Criar tarefas com atributos
print("Criando tarefas...")
tasks = create_test_tasks(process, users, resources)

# 6. Criar regras de concorrência
print("Criando regras de concorrência...")
rules = create_concurrency_rules(process)

# 7. Testar verificação de concorrência
print("\nTestando verificação de concorrência:")
plumbing = tasks['plumbing']
electrical = tasks['electrical']
painting = tasks['painting']
flooring = tasks['flooring']

can_run, reason = can_tasks_run_concurrently(plumbing, electrical)
print(
    f"Encanamento e Elétrica podem ser executadas concorrentemente? {can_run}. Razão: {reason}")

can_run, reason = can_tasks_run_concurrently(painting, flooring)
print(
    f"Pintura e Piso podem ser executadas concorrentemente? {can_run}. Razão: {reason}")

# 8. Testar fluxo de aprovação
print("\nTestando fluxo de aprovação:")
# Criar solicitação de alteração
change_request = ChangeRequest.objects.create(
    process=process,
    requested_by=users['electrician'],
    description="Reordenar tarefa elétrica para ser executada antes do encanamento",
    changes={
        'task_id': electrical.id,
        'old_order': electrical.order,
        'new_order': 25  # Entre estrutura e encanamento
    },
    status='pending'
)

print(f"Solicitação de alteração criada: {change_request}")

# Simular aprovação
success, message = apply_change_request(
    change_request, users['project_manager'])
print(f"Aplicação da alteração: {success}. Mensagem: {message}")
print(f"Status da solicitação após aprovação: {change_request.status}")

# Verificar se a ordem foi atualizada
electrical.refresh_from_db()
print(f"Nova ordem da tarefa elétrica: {electrical.order}")

print("\nTeste concluído com sucesso!")
