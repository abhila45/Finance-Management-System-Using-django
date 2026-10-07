from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm

def transaction_list(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    qs = Transaction.objects.filter(user=request.user)
    t_type = request.GET.get("type")
    if t_type:
        qs = qs.filter(transaction_type=t_type)
    return render(request, "transactions/transaction_list.html", {"transactions": qs})

def transaction_create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.method == "POST":
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            messages.success(request, "Transaction created successfully!")
            return redirect("transactions:list")
    else:
        form = TransactionForm(user=request.user)
    return render(request, "transactions/transaction_form.html", {"form": form, "action": "Add"})

def transaction_update(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=t, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully!")
            return redirect("transactions:list")
    else:
        form = TransactionForm(instance=t, user=request.user)
    return render(request, "transactions/transaction_form.html", {"form": form, "action": "Edit", "transaction": t})

def transaction_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        t.delete()
        messages.success(request, "Transaction deleted successfully!")
        return redirect("transactions:list")
    return render(request, "transactions/transaction_confirm_delete.html", {"transaction": t})

def category_list(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    cats = Category.objects.filter(user=request.user) | Category.objects.filter(user__isnull=True)
    return render(request, "transactions/category_list.html", {"categories": cats})

def category_create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.user = request.user
            c.save()
            messages.success(request, "Category created successfully!")
            return redirect("transactions:category_list")
    else:
        form = CategoryForm()
    return render(request, "transactions/category_form.html", {"form": form})

def category_update(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("transactions:category_list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "transactions/category_form.html", {"form": form, "action": "Edit", "category": category})

def category_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect("transactions:category_list")
    return render(request, "transactions/category_confirm_delete.html", {"category": category})