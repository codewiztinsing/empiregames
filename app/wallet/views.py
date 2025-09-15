from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Transaction, WithdrawalRequest

# Create your views here.
def transaction_details(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    return render(request, 'dashboard/transaction_details.html', {'transaction': transaction})


def withdrawal_request_details(request, withdrawal_request_id):
    withdrawal_request = WithdrawalRequest.objects.get(id=withdrawal_request_id)
    return render(request, 'dashboard/withdrawal_request_details.html', {'withdrawal_request': withdrawal_request})

def withdrawal_request_list(request):
    withdrawal_requests = WithdrawalRequest.objects.all()
    paginator = Paginator(withdrawal_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_withdrawal_requests = withdrawal_requests.count()
    has_next = page_obj.has_next()
    has_previous = page_obj.has_previous()
    next_page = page_obj.next_page_number() if has_next else None
    previous_page = page_obj.previous_page_number() if has_previous else None
    context = {
        'withdrawal_requests': page_obj,
        'total_withdrawal_requests': total_withdrawal_requests,
        'has_next': has_next,
        'has_previous': has_previous,
        'next_page': next_page,
        'previous_page': previous_page,
    }
    return render(request, 'dashboard/payments.html', context)

def approve_withdrawal_request(request, withdrawal_request_id):
    withdrawal_request = WithdrawalRequest.objects.get(id=withdrawal_request_id)
    withdrawal_request.status = "success"
    withdrawal_request.save()
    return redirect('dashboard:withdrawal_request_list')

def reject_withdrawal_request(request, withdrawal_request_id):
    withdrawal_request = WithdrawalRequest.objects.get(id=withdrawal_request_id)
    withdrawal_request.status = "failed"
    withdrawal_request.save()
    return redirect('dashboard:withdrawal_request_list')