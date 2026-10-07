from django.contrib import admin
from .models import Budget

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "amount", "period", "start_date", "end_date", "created_at"]
    list_filter = ["period", "created_at"]
    search_fields = ["name", "user__username"]
