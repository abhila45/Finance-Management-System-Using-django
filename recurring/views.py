from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import RecurringTransaction, RecurringTransactionLog
from .forms import RecurringTransactionForm
from transactions.models import Transaction
from datetime import date, timedelta


@login_required
def recurring_list(request):
    """List all recurring transactions for the user"""
    recurring = RecurringTransaction.objects.filter(user=request.user)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        recurring = recurring.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        recurring = recurring.filter(transaction_type=type_filter)
    
    return render(request, 'recurring/recurring_list.html', {
        'recurring_transactions': recurring,
        'status_filter': status_filter,
        'type_filter': type_filter,
    })


@login_required
def recurring_create(request):
    """Create a new recurring transaction"""
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            recurring = form.save(commit=False)
            recurring.user = request.user
            recurring.next_due_date = recurring.start_date
            recurring.save()
            messages.success(request, 'Recurring transaction created successfully!')
            return redirect('recurring:list')
    else:
        form = RecurringTransactionForm(user=request.user)
    
    return render(request, 'recurring/recurring_form.html', {
        'form': form,
        'action': 'Add'
    })


@login_required
def recurring_update(request, pk):
    """Update an existing recurring transaction"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = RecurringTransactionForm(request.POST, instance=recurring, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recurring transaction updated successfully!')
            return redirect('recurring:list')
    else:
        form = RecurringTransactionForm(instance=recurring, user=request.user)
    
    return render(request, 'recurring/recurring_form.html', {
        'form': form,
        'action': 'Edit',
        'recurring': recurring
    })


@login_required
def recurring_delete(request, pk):
    """Delete a recurring transaction"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        recurring.delete()
        messages.success(request, 'Recurring transaction deleted successfully!')
        return redirect('recurring:list')
    
    return render(request, 'recurring/recurring_confirm_delete.html', {
        'recurring': recurring
    })


@login_required
def recurring_pause(request, pk):
    """Pause a recurring transaction"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    recurring.status = 'paused'
    recurring.save()
    messages.success(request, 'Recurring transaction paused successfully!')
    return redirect('recurring:list')


@login_required
def recurring_resume(request, pk):
    """Resume a paused recurring transaction"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    recurring.status = 'active'
    recurring.next_due_date = recurring.calculate_next_due_date()
    recurring.save()
    messages.success(request, 'Recurring transaction resumed successfully!')
    return redirect('recurring:list')


@login_required
def recurring_detail(request, pk):
    """View details of a recurring transaction and its generation history"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    logs = recurring.logs.all()[:20]  # Last 20 generations
    
    return render(request, 'recurring/recurring_detail.html', {
        'recurring': recurring,
        'logs': logs
    })


@login_required
def generate_transaction(request, pk):
    """Manually generate a transaction from a recurring template"""
    recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Create the actual transaction
        transaction = Transaction.objects.create(
            user=request.user,
            title=recurring.title,
            amount=recurring.amount,
            transaction_type=recurring.transaction_type,
            category=recurring.category,
            date=recurring.next_due_date,
            description=f"Generated from recurring transaction: {recurring.description or ''}"
        )
        
        # Create log entry
        RecurringTransactionLog.objects.create(
            recurring_transaction=recurring,
            generated_transaction=transaction,
            due_date=recurring.next_due_date,
            notes='Manually generated'
        )
        
        # Update recurring transaction
        recurring.last_generated = recurring.next_due_date
        recurring.next_due_date = recurring.calculate_next_due_date()
        
        # Check if we've reached the end date
        if recurring.end_date and recurring.next_due_date > recurring.end_date:
            recurring.status = 'completed'
        
        recurring.save()
        
        messages.success(request, 'Transaction generated successfully!')
        return redirect('recurring:detail', pk=pk)
    
    return render(request, 'recurring/generate_confirm.html', {
        'recurring': recurring
    })
