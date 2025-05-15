from django.db import models

class ConcurrencyRule(models.Model):
    RULE_TYPES = (
        ('same_responsible', 'Mesmo Responsável'),
        ('resource_conflict', 'Conflito de Recurso'),
        ('custom', 'Regra Personalizada'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    process = models.ForeignKey('Process', on_delete=models.CASCADE, related_name='concurrency_rules')
    custom_condition = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"