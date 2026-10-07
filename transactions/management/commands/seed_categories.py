from django.core.management.base import BaseCommand
from transactions.models import Category

class Command(BaseCommand):
    help = 'Seed default categories for income and expenses'

    def handle(self, *args, **kwargs):
        default_income_categories = [
            'Salary',
            'Freelance',
            'Investments',
            'Gifts',
            'Other Income',
        ]

        default_expense_categories = [
            'Food & Dining',
            'Transportation',
            'Shopping',
            'Entertainment',
            'Bills & Utilities',
            'Healthcare',
            'Education',
            'Travel',
            'Other Expenses',
        ]

        # Create income categories
        for name in default_income_categories:
            Category.objects.get_or_create(
                name=name,
                transaction_type='income',
                user=None
            )
            self.stdout.write(f'Created income category: {name}')

        # Create expense categories
        for name in default_expense_categories:
            Category.objects.get_or_create(
                name=name,
                transaction_type='expense',
                user=None
            )
            self.stdout.write(f'Created expense category: {name}')

        self.stdout.write(self.style.SUCCESS('Default categories seeded successfully!'))