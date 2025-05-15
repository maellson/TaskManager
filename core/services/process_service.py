from django.utils import timezone
from ..models import ChangeRequest


def apply_change_request(change_request: ChangeRequest, approver):
    """
    Aplica as alterações de uma solicitação de mudança
    """
    if change_request.status != 'pending':
        return False, "Esta solicitação não está pendente"
    
    changes = change_request.changes
    
    # Implementar lógica para aplicar alterações
    # Exemplo: reordenar uma tarefa
    if 'task_id' in changes and 'new_order' in changes:
        from ..models import Task
        from .task_service import is_valid_task_order
        
        try:
            task = Task.objects.get(id=changes['task_id'])
            
            # Verificar se a nova ordem ainda é válida
            is_valid, message = is_valid_task_order(task, changes['new_order'])
            if not is_valid:
                change_request.status = 'rejected'
                change_request.approved_by = approver
                change_request.response_date = timezone.now()
                change_request.save()
                return False, message
            
            task.order = changes['new_order']
            task.save()
        except Task.DoesNotExist:
            return False, "Tarefa não encontrada"
    
    # Atualizar solicitação de alteração
    change_request.status = 'approved'
    change_request.approved_by = approver
    change_request.response_date = timezone.now()
    change_request.save()
    
    return True, "Alterações aplicadas com sucesso"

def clone_process(process, user):
    """
    Clona um processo existente com todas as suas tarefas
    """
    from ..models import Process, Task, TaskDependency
    
    # Criar novo processo
    new_process = Process.objects.create(
        name=f"Cópia de {process.name}",
        description=process.description,
        created_by=user,
        updated_by=user
    )
    
    # Mapeamento de IDs de tarefas antigas para novas
    task_mapping = {}
    
    # Clonar tarefas
    for task in process.tasks.all():
        new_task = Task.objects.create(
            process=new_process,
            name=task.name,
            description=task.description,
            responsible=task.responsible,
            planned_start_date=task.planned_start_date,
            planned_end_date=task.planned_end_date,
            status='not_started',
            is_active=task.is_active,
            order=task.order
        )
        task_mapping[task.id] = new_task.id
    
    # Clonar dependências
    for dependency in TaskDependency.objects.filter(task__process=process):
        if dependency.task.id in task_mapping and dependency.prerequisite_task.id in task_mapping:
            TaskDependency.objects.create(
                task_id=task_mapping[dependency.task.id],
                prerequisite_task_id=task_mapping[dependency.prerequisite_task.id]
            )
    
    return new_process