from ..models import Task, TaskDependency, ConcurrencyRule
from django.db.models import Q
from django.utils import timezone

def can_tasks_run_concurrently(task1, task2):
    """
    Verifica se duas tarefas podem ser executadas concorrentemente
    """
    # Verificar se as tarefas são do mesmo processo
    if task1.process_id != task2.process_id:
        return False, "Tarefas pertencem a processos diferentes"
    
    # Verificar dependências diretas
    if TaskDependency.objects.filter(
        Q(task=task1, prerequisite_task=task2) | 
        Q(task=task2, prerequisite_task=task1)
    ).exists():
        return False, "Existe uma dependência direta entre as tarefas"
    
    # Verificar regras de concorrência ativas
    rules = ConcurrencyRule.objects.filter(
        process=task1.process,
        is_active=True
    )
    
    for rule in rules:
        if rule.rule_type == 'same_responsible':
            # Verificar se as tarefas têm o mesmo responsável
            if task1.responsible and task2.responsible and task1.responsible_id == task2.responsible_id:
                return False, "As tarefas têm o mesmo responsável"
        
        elif rule.rule_type == 'resource_conflict':
            # Verificar conflitos de recursos
            pass
        
        elif rule.rule_type == 'custom':
            # Avaliar regra personalizada (JSON)
            pass
    
    return True, "As tarefas podem ser executadas concorrentemente"

def is_valid_task_order(task, new_order):
    """
    Verifica se uma nova ordem para uma tarefa é válida baseada em suas dependências
    """
    # Obter todas as tarefas do mesmo processo
    process_tasks = Task.objects.filter(process=task.process).exclude(id=task.id)
    
    # Obter tarefas das quais a tarefa atual depende
    prerequisite_tasks = task.dependencies.all().values_list('prerequisite_task', flat=True)
    prerequisite_tasks = Task.objects.filter(id__in=prerequisite_tasks)
    
    # Obter tarefas que dependem da tarefa atual
    dependent_tasks = task.dependent_tasks.all().values_list('task', flat=True)
    dependent_tasks = Task.objects.filter(id__in=dependent_tasks)
    
    # Verificar se a nova ordem respeita as dependências
    for prereq in prerequisite_tasks:
        if prereq.order >= new_order:
            return False, f"A tarefa '{task.name}' não pode vir antes da tarefa '{prereq.name}' que é um pré-requisito"
    
    for dep in dependent_tasks:
        if dep.order <= new_order:
            return False, f"A tarefa '{task.name}' não pode vir depois da tarefa '{dep.name}' que depende dela"
    
    return True, "A nova ordem é válida"

def get_critical_path(process):
    """
    Calcula o caminho crítico de um processo
    """
    # Algoritmo de caminho crítico
    pass