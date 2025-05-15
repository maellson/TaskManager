from django.db import models

class ApprovalLevel(models.Model):
    name = models.CharField(max_length=255)
    level = models.PositiveSmallIntegerField(help_text="Nível hierárquico (1=baixo, 10=alto)")
    description = models.TextField(blank=True)
    required_approvers = models.PositiveSmallIntegerField(default=1, help_text="Número de aprovadores necessários")
    
    def __str__(self):
        return f"{self.name} (Nível {self.level})"

class ApprovalAuthority(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='approval_authorities')
    level = models.ForeignKey('ApprovalLevel', on_delete=models.CASCADE, related_name='authorized_users')
    processes = models.ManyToManyField('Process', blank=True, related_name='approval_authorities')
    
    class Meta:
        unique_together = ('user', 'level')
        verbose_name_plural = "Approval Authorities"
    
    def __str__(self):
        return f"{self.user.username} - {self.level.name}"