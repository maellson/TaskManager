from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcessViewSet, TaskViewSet, ConcurrencyRuleViewSet, ChangeRequestViewSet

router = DefaultRouter()
router.register(r'processes', ProcessViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'concurrency-rules', ConcurrencyRuleViewSet)
router.register(r'change-requests', ChangeRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
