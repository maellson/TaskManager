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