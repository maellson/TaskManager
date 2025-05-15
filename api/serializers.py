from rest_framework import serializers
from core.models import Process, Task, TaskDependency, ConcurrencyRule, ChangeRequest
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type']

class TaskDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDependency
        fields = ['id', 'prerequisite_task']

class TaskSerializer(serializers.ModelSerializer):
    dependencies = TaskDependencySerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'responsible', 'start_date', 'end_date', 
                  'planned_start_date', 'planned_end_date', 'status', 'is_active', 
                  'order', 'dependencies', 'process']

class ProcessSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Process
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 
                  'is_active', 'created_by', 'tasks']

class ConcurrencyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcurrencyRule
        fields = ['id', 'name', 'description', 'rule_type', 'process', 
                  'custom_condition', 'is_active']

class ChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeRequest
        fields = ['id', 'process', 'requested_by', 'approved_by', 'status',
                  'request_date', 'response_date', 'description', 'changes']