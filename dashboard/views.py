from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from transactions.models import Transaction
from .models import Budget
from .forms import BudgetForm
from datetime import date

def home(request):
    if not request.user.is_authenticated:
        return render(request, "dashboard/landing.html")
    
    qs = Transaction.objects.filter(user=request.user)

    total_income = qs.filter(transaction_type="income").aggregate(Sum("amount"))["amount__sum"] or 0
    total_expense = qs.filter(transaction_type="expense").aggregate(Sum("amount"))["amount__sum"] or 0
    balance = total_income - total_expense

    recent_transactions = qs.order_by("-date", "-created_at")[:10]

    # simple category breakdown for expenses
    expense_by_category = (
        qs.filter(transaction_type="expense")
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    # Get active budgets
    today = date.today()
    active_budgets = Budget.objects.filter(
        user=request.user,
        start_date__lte=today,
        end_date__gte=today
    )

    return render(
        request,
        "dashboard/home.html",
        {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "recent_transactions": recent_transactions,
            "expense_by_category": expense_by_category,
            "active_budgets": active_budgets,
        },
    )

def budget_list(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    budgets = Budget.objects.filter(user=request.user)
    return render(request, "dashboard/budget_list.html", {"budgets": budgets})

def budget_create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, "Budget created successfully!")
            return redirect("dashboard:budget_list")
    else:
        form = BudgetForm()
    return render(request, "dashboard/budget_form.html", {"form": form, "action": "Add"})

def budget_update(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated successfully!")
            return redirect("dashboard:budget_list")
    else:
        form = BudgetForm(instance=budget)
    return render(request, "dashboard/budget_form.html", {"form": form, "action": "Edit", "budget": budget})

def budget_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == "POST":
        budget.delete()
        messages.success(request, "Budget deleted successfully!")
        return redirect("dashboard:budget_list")
    return render(request, "dashboard/budget_confirm_delete.html", {"budget": budget})