from django.urls import path
from .views import ConfigGeneratorView

urlpatterns = [
    path('generate-config/', ConfigGeneratorView.as_view(), name='generate-config'),
]