from django.urls import path
from . import views

app_name = 'recurring'

urlpatterns = [
    path('', views.recurring_list, name='list'),
    path('add/', views.recurring_create, name='create'),
    path('<int:pk>/edit/', views.recurring_update, name='update'),
    path('<int:pk>/delete/', views.recurring_delete, name='delete'),
    path('<int:pk>/pause/', views.recurring_pause, name='pause'),
    path('<int:pk>/resume/', views.recurring_resume, name='resume'),
    path('<int:pk>/detail/', views.recurring_detail, name='detail'),
    path('<int:pk>/generate/', views.generate_transaction, name='generate'),
]
