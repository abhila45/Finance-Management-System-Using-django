from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("budgets/", views.budget_list, name="budget_list"),
    path("budgets/add/", views.budget_create, name="budget_create"),
    path("budgets/<int:pk>/edit/", views.budget_update, name="budget_update"),
    path("budgets/<int:pk>/delete/", views.budget_delete, name="budget_delete"),
]