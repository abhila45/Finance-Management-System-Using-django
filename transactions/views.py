from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm

def transaction_list(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    qs = Transaction.objects.filter(user=request.user)

    # Filter by type
    t_type = request.GET.get("type")
    if t_type:
        qs = qs.filter(transaction_type=t_type)

    # Search by title
    search = request.GET.get("search")
    if search:
        qs = qs.filter(title__icontains=search)

    # Filter by category
    category = request.GET.get("category")
    if category:
        qs = qs.filter(category_id=category)

    # Filter by date range
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)

    # Filter by amount range
    min_amount = request.GET.get("min_amount")
    max_amount = request.GET.get("max_amount")
    if min_amount:
        qs = qs.filter(amount__gte=min_amount)
    if max_amount:
        qs = qs.filter(amount__lte=max_amount)

    # Filter by currency
    currency = request.GET.get("currency")
    if currency:
        qs = qs.filter(currency=currency)

    # Get all categories for filter dropdown
    categories = Category.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    )

    return render(request, "transactions/transaction_list.html", {
        "transactions": qs,
        "categories": categories,
        "search": search,
        "t_type": t_type,
        "category": category,
        "start_date": start_date,
        "end_date": end_date,
        "min_amount": min_amount,
        "max_amount": max_amount,
        "currency": currency,
    })

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


@login_required
def export_csv(request):
    """Export transactions to CSV"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Type', 'Category', 'Date', 'Description'])

    for transaction in transactions:
        writer.writerow([
            transaction.title,
            transaction.amount,
            transaction.transaction_type,
            transaction.category.name if transaction.category else '',
            transaction.date,
            transaction.description
        ])

    return response


@login_required
def export_pdf(request):
    """Export transactions to PDF"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("Transaction Report", styles['Title'])
    elements.append(title)

    # Table data
    data = [['Title', 'Amount', 'Type', 'Category', 'Date']]
    for transaction in transactions[:50]:  # Limit to 50 transactions for PDF
        data.append([
            transaction.title,
            str(transaction.amount),
            transaction.transaction_type,
            transaction.category.name if transaction.category else 'N/A',
            str(transaction.date)
        ])

    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    return response