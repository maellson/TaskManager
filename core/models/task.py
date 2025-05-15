from django.db import models

class Task(models.Model):
    TASK_TYPES = (
        ('foundation', 'Fundação'),
        ('structure', 'Estrutura'),
        ('plumbing', 'Encanamento'),
        ('electrical', 'Elétrico'),
        ('painting', 'Pintura'),
        ('flooring', 'Piso'),
        ('finishing', 'Acabamento'),
        ('other', 'Outro'),
    )
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, default='other')
    location = models.CharField(max_length=255, blank=True, help_text="Localização onde a tarefa será executada")
    STATUS_CHOICES = (
        ('not_started', 'Não Iniciada'),
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluída'),
        ('blocked', 'Bloqueada'),
    )
    
    process = models.ForeignKey('Process', on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    responsible = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='responsible_tasks')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    planned_start_date = models.DateTimeField(null=True, blank=True)
    planned_end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)  # Para ordenação manual
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.process.name})"
    
    class Meta:
        ordering = ['process', 'order']

class TaskDependency(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='dependencies')
    prerequisite_task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='dependent_tasks')
    
    class Meta:
        unique_together = ('task', 'prerequisite_task')