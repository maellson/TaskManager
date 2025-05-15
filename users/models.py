from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPES = (
        ('project_manager', 'Gerente de Projeto'),
        ('project_leader', 'Líder de Projetos'),
        ('regular', 'Usuário Regular'),
    )
    user_type = models.CharField(
        max_length=20, choices=USER_TYPES, default='regular')

    class Meta:
        permissions = [
            ('can_approve_changes', 'Pode aprovar mudanças na ordem das tarefas'),
            ('can_modify_processes', 'Pode modificar a estrutura de processos'),
        ]
