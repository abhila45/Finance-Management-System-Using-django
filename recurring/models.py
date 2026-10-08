from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from transactions.models import Category


class RecurringTransaction(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_transactions')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    transaction_type = models.CharField(max_length=10, choices=[
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='recurring_transactions')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank for unlimited")
    last_generated = models.DateField(null=True, blank=True)
    next_due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    reminder_days = models.IntegerField(default=3, help_text="Days before due date to send reminder")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['next_due_date']
        verbose_name = "Recurring Transaction"
        verbose_name_plural = "Recurring Transactions"

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.frequency})"

    def calculate_next_due_date(self):
        """Calculate the next due date based on frequency"""
        from datetime import timedelta, date
        from dateutil.relativedelta import relativedelta

        base_date = self.last_generated if self.last_generated else self.start_date

        if self.frequency == 'daily':
            return base_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return base_date + timedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return base_date + timedelta(weeks=2)
        elif self.frequency == 'monthly':
            return base_date + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return base_date + relativedelta(months=3)
        elif self.frequency == 'yearly':
            return base_date + relativedelta(years=1)
        return base_date

    def is_due(self):
        """Check if transaction is due today or overdue"""
        from datetime import date
        return self.next_due_date <= date.today()

    def should_generate(self):
        """Check if a new transaction should be generated"""
        from datetime import date
        return self.status == 'active' and self.is_due() and (
            not self.end_date or self.next_due_date <= self.end_date
        )


class RecurringTransactionLog(models.Model):
    """Track when recurring transactions are generated"""
    recurring_transaction = models.ForeignKey(RecurringTransaction, on_delete=models.CASCADE, related_name='logs')
    generated_transaction = models.ForeignKey('transactions.Transaction', on_delete=models.SET_NULL, null=True, related_name='recurring_log')
    generated_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-generated_date']
        verbose_name = "Recurring Transaction Log"
        verbose_name_plural = "Recurring Transaction Logs"

    def __str__(self):
        return f"{self.recurring_transaction.title} - {self.generated_date}"
