from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.db import models
from transactions.models import Transaction, Category
from datetime import date, timedelta
from collections import defaultdict
import calendar


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard with charts and insights"""
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    
    # Date range filters
    period = request.GET.get('period', '30')  # default 30 days
    days = int(period)
    start_date = date.today() - timedelta(days=days)
    filtered_transactions = transactions.filter(date__gte=start_date)
    
    # Basic statistics
    total_income = filtered_transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = filtered_transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_income - total_expense
    
    # Monthly trend data
    monthly_data = (
        filtered_transactions
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(
            income=Sum('amount', filter=Q(transaction_type='income')),
            expense=Sum('amount', filter=Q(transaction_type='expense'))
        )
        .order_by('month')
    )
    
    # Category breakdown
    category_breakdown = (
        filtered_transactions
        .filter(transaction_type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    
    # Daily spending trend
    daily_data = (
        filtered_transactions
        .filter(transaction_type='expense')
        .annotate(day=TruncDay('date'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )
    
    # Average daily spending
    avg_daily_spending = (
        filtered_transactions
        .filter(transaction_type='expense')
        .aggregate(avg=Sum('amount') / Count('date', distinct=True))
    )['avg'] or 0
    
    # Top spending categories
    top_categories = category_breakdown[:5]
    
    # Income vs Expense by category
    income_by_category = (
        filtered_transactions
        .filter(transaction_type='income')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    
    context = {
        'period': period,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'monthly_data': list(monthly_data),
        'category_breakdown': list(category_breakdown),
        'daily_data': list(daily_data),
        'avg_daily_spending': avg_daily_spending,
        'top_categories': list(top_categories),
        'income_by_category': list(income_by_category),
        'transaction_count': filtered_transactions.count(),
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def spending_trends(request):
    """Detailed spending trends analysis"""
    user = request.user
    transactions = Transaction.objects.filter(user=user, transaction_type='expense')
    
    # Group by category
    category_spending = (
        transactions
        .values('category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    
    # Group by month
    monthly_spending = (
        transactions
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    
    return render(request, 'analytics/spending_trends.html', {
        'category_spending': list(category_spending),
        'monthly_spending': list(monthly_spending),
    })


@login_required
def income_analysis(request):
    """Income sources analysis"""
    user = request.user
    transactions = Transaction.objects.filter(user=user, transaction_type='income')
    
    # Income by category
    income_by_category = (
        transactions
        .values('category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    
    # Monthly income trend
    monthly_income = (
        transactions
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    
    return render(request, 'analytics/income_analysis.html', {
        'income_by_category': list(income_by_category),
        'monthly_income': list(monthly_income),
    })
