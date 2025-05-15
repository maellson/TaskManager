from django.contrib import admin
from .models import Process, Task, TaskDependency, ConcurrencyRule, ChangeRequest

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'process', 'status', 'responsible', 'start_date', 'end_date')
    list_filter = ('status', 'is_active', 'process')
    search_fields = ('name', 'description')

@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ('task', 'prerequisite_task')
    list_filter = ('task__process',)

@admin.register(ConcurrencyRule)
class ConcurrencyRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'process', 'is_active')
    list_filter = ('rule_type', 'is_active', 'process')

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('process', 'requested_by', 'status', 'request_date')
    list_filter = ('status', 'process')
    search_fields = ('description',)