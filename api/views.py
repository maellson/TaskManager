from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from core.models import Process, Task, TaskDependency, ConcurrencyRule, ChangeRequest
from .serializers import (ProcessSerializer, TaskSerializer, ConcurrencyRuleSerializer,
                          ChangeRequestSerializer)
from core.services.task_service import can_tasks_run_concurrently, is_valid_task_order, get_critical_path
from core.services.process_service import apply_change_request, clone_process


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]#liberado apenas para testes. hsbilitei pra ver o flow funcionando

    @action(detail=True, methods=['get'])
    def critical_path(self, request, pk=None):
        process = self.get_object()
        path = get_critical_path(process)
        return Response(path)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        process = self.get_object()
        new_process = clone_process(process, request.user)
        serializer = self.get_serializer(new_process)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def flow_data(self, request, pk=None):
        """
        Retorna dados formatados para visualização em React Flow
        """
        process = self.get_object()

        # Obter todas as tarefas
        tasks = process.tasks.all().prefetch_related(
            'dependencies', 'resources', 'responsible')

        # Preparar nós (tarefas)
        nodes = []
        task_id_map = {}  # Mapear task.id para índice no array de nodes

        for i, task in enumerate(tasks):
            task_id_map[task.id] = i
            responsible_name = task.responsible.get_full_name(
            ) if task.responsible else "Não atribuído"

            # Preparar informações dos recursos
            resources = []
            for tr in task.resources.all():
                resources.append({
                    'name': tr.resource.name,
                    'quantity': float(tr.quantity_allocated),
                    'unit': tr.resource.unit
                })

            # Criar nó
            nodes.append({
                'id': str(task.id),
                'type': 'taskNode',  # Tipo personalizado que criaremos no React
                # Posição baseada na ordem
                'position': {'x': i * 250, 'y': task.order * 100},
                'data': {
                    'id': task.id,
                    'name': task.name,
                    'type': task.task_type,
                    'status': task.status,
                    'responsible': responsible_name,
                    'location': task.location,
                    'resources': resources,
                    'start_date': task.planned_start_date.isoformat() if task.planned_start_date else None,
                    'end_date': task.planned_end_date.isoformat() if task.planned_end_date else None,
                    'order': task.order
                }
            })

        # Preparar arestas (dependências)
        edges = []
        for task in tasks:
            for dep in task.dependencies.all():
                edges.append({
                    'id': f'e{dep.prerequisite_task.id}-{task.id}',
                    'source': str(dep.prerequisite_task.id),
                    'target': str(task.id),
                    'animated': True,
                    'label': 'depende de'
                })

        # Preparar regras de concorrência
        concurrency_rules = []
        for rule in process.concurrency_rules.all():
            concurrency_rules.append({
                'id': rule.id,
                'name': rule.name,
                'type': rule.rule_type,
                'description': rule.description,
                'custom_condition': rule.custom_condition
            })

        return Response({
            'nodes': nodes,
            'edges': edges,
            'concurrency_rules': concurrency_rules
        })


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=True, methods=['post'])
    def add_dependency(self, request, pk=None):
        task = self.get_object()
        prerequisite_id = request.data.get('prerequisite_id')

        try:
            prerequisite = Task.objects.get(pk=prerequisite_id)
            dependency = TaskDependency.objects.create(
                task=task,
                prerequisite_task=prerequisite
            )
            return Response({'status': 'dependência adicionada'})
        except Task.DoesNotExist:
            return Response({'error': 'Tarefa pré-requisito não encontrada'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_dependency(self, request, pk=None):
        task = self.get_object()
        prerequisite_id = request.data.get('prerequisite_id')

        try:
            dependency = TaskDependency.objects.get(
                task=task,
                prerequisite_task_id=prerequisite_id
            )
            dependency.delete()
            return Response({'status': 'dependência removida'})
        except TaskDependency.DoesNotExist:
            return Response({'error': 'Dependência não encontrada'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        task = self.get_object()
        new_order = request.data.get('new_order')
        user = request.user

        # Verificar se a nova ordem é válida
        is_valid, message = is_valid_task_order(task, new_order)

        if not is_valid:
            return Response({
                'status': 'erro',
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se usuário tem permissão para reordenar diretamente
        if user.user_type == 'project_manager' or user.has_perm('core.can_modify_processes'):
            task.order = new_order
            task.save()
            return Response({'status': 'tarefa reordenada'})
        else:
            # Criar solicitação de alteração
            change_request = ChangeRequest.objects.create(
                process=task.process,
                requested_by=user,
                description=f"Reordenar tarefa {task.name}",
                changes={
                    'task_id': task.id,
                    'old_order': task.order,
                    'new_order': new_order
                }
            )
            return Response({
                'status': 'solicitação de alteração criada',
                'change_request_id': change_request.id
            })

    @action(detail=False, methods=['post'])
    def can_run_concurrently(self, request):
        task1_id = request.data.get('task1_id')
        task2_id = request.data.get('task2_id')

        try:
            task1 = Task.objects.get(pk=task1_id)
            task2 = Task.objects.get(pk=task2_id)

            result, reason = can_tasks_run_concurrently(task1, task2)

            return Response({
                'can_run_concurrently': result,
                'reason': reason
            })
        except Task.DoesNotExist:
            return Response({'error': 'Uma ou ambas as tarefas não foram encontradas'},
                            status=status.HTTP_404_NOT_FOUND)


class ConcurrencyRuleViewSet(viewsets.ModelViewSet):
    queryset = ConcurrencyRule.objects.all()
    serializer_class = ConcurrencyRuleSerializer


class ChangeRequestViewSet(viewsets.ModelViewSet):
    queryset = ChangeRequest.objects.all()
    serializer_class = ChangeRequestSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        change_request = self.get_object()
        user = request.user

        # Verificar permissões
        if not (user.user_type == 'project_manager' or user.has_perm('core.can_approve_changes')):
            return Response({'error': 'Você não tem permissão para aprovar alterações'},
                            status=status.HTTP_403_FORBIDDEN)

        success, message = apply_change_request(change_request, user)

        return Response({'status': 'solicitação aprovada', 'message': message})
