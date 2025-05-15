from django.db import models

class Process(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_processes')
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='updated_processes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ChangeRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Aguardando Aprovação'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    )
    
    process = models.ForeignKey('Process', on_delete=models.CASCADE, related_name='change_requests')
    requested_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='requested_changes')
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_changes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField()
    changes = models.JSONField()  # Armazena detalhes das alterações
    
    def __str__(self):
        return f"Solicitação de alteração para {self.process.name} ({self.get_status_display()})"