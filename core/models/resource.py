
from django.db import models

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('material', 'Material'),
        ('equipment', 'Equipamento'),
        ('human', 'Humano'),
        ('service', 'Serviço'),
    )
    
    name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True)
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"

class ProcessResource(models.Model):
    process = models.ForeignKey('Process', on_delete=models.CASCADE, related_name='resources')
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE, related_name='process_allocations')
    quantity_allocated = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('process', 'resource')
    
    def __str__(self):
        return f"{self.resource.name} para {self.process.name}"

class TaskResource(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='resources')
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE, related_name='task_allocations')
    quantity_allocated = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('task', 'resource')
    
    def __str__(self):
        return f"{self.resource.name} para {self.task.name}"