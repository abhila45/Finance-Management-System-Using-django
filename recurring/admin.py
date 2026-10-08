from django.contrib import admin
from .models import RecurringTransaction, RecurringTransactionLog


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'transaction_type', 'frequency', 'status', 'next_due_date']
    list_filter = ['status', 'transaction_type', 'frequency']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RecurringTransactionLog)
class RecurringTransactionLogAdmin(admin.ModelAdmin):
    list_display = ['recurring_transaction', 'generated_date', 'due_date']
    readonly_fields = ['generated_date']
