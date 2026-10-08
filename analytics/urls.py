from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('spending-trends/', views.spending_trends, name='spending_trends'),
    path('income-analysis/', views.income_analysis, name='income_analysis'),
]
