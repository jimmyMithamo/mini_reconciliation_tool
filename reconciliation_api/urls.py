from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApiView.as_view(), name='api_view'),
    path('reconciliation/', views.ReconciliationView.as_view(), name='reconciliation_view'),
]
