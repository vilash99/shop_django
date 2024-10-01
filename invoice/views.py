
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Sum, F, Q
from django.core.paginator import Paginator

from django.utils.decorators import method_decorator

from invoice.models import (
    Profile, Party, ItemService, Sale, Transaction, PartyBalance
)
from invoice.forms import (
    PartyForm, ItemsForm, ServiceForm, InvoiceForm,
    TransactionItemForm, TransactionServiceForm, PartyBalanceForm
)


def index(request):
    return render(request, 'common/index.html')


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profile
    template_name = 'common/profile.html'
    fields = ['name', 'phone', 'address', 'reg_no']
    success_message = 'Company details are updated successfully!'


class PartiesView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Show Parties details with total billed for all invoices
    """
    model = Party
    template_name = 'party/parties.html'
    form_class = PartyForm
    success_message = 'New Party saved successfully!'
    paginate_by = 50
    page_kwarg = 'page'

    def querystring(self):
        qs = self.request.GET.copy()
        qs.pop(self.page_kwarg, None)
        return qs.urlencode()

    def get_queryset(self):
        # Show all transaction with total purchase for all parties
        search_txt = self.request.GET.get('q', '')

        qs = Party.objects.annotate(
            total_bill=Sum('sales__total_amount')
        ).filter(name__icontains=search_txt).order_by('name')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        party_list = self.get_queryset()
        query = self.querystring()

        paginator = Paginator(party_list, self.paginate_by)
        page_number = self.request.GET.get('page', '')
        party_list = paginator.get_page(page_number)

        context.update({
            'page_obj': party_list,
            'query': query,
        })
        return context


class SinglePartyView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View and edit single party details and display related transactions.
    """
    model = Party
    template_name = 'party/update-party.html'
    fields = ['name', 'phone', 'address']
    success_message = 'Party updated successfully!'
    paginate_by = 50
    page_kwarg = 'page'

    def querystring(self):
        qs = self.request.GET.copy()
        qs.pop(self.page_kwarg, None)
        return qs.urlencode()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        party = self.get_object()
        transactions = PartyBalance.objects.filter(party=party).order_by('-pay_date')

        paginator = Paginator(transactions, self.paginate_by)
        page_number = self.request.GET.get(self.page_kwarg, 1)
        transactions_page = paginator.get_page(page_number)

        query = self.querystring()

        context.update({
            'page_obj': transactions_page,
            'party': party,
            'query': query,
        })
        return context


class PartyBalanceView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Add new balance entry for a party and show all balances for parties.
    """
    # Has Signal to update 'balance_amount when 'PartyBalance' is added/updated/deleted

    model = PartyBalance
    template_name = 'party/balance_payment.html'
    form_class = PartyBalanceForm
    success_message = 'Party balance is paid successfully!'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get the party instance based on the URL parameter
        party = get_object_or_404(Party, pk=self.kwargs['pk'])
        # Pass the party instance to the form
        kwargs['party'] = party
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        party = get_object_or_404(Party, pk=self.kwargs['pk'])
        context.update({
            'party_id': self.kwargs['pk'],
            'party': party,
        })
        return context


class StockView(LoginRequiredMixin, ListView):
    """
    Add new product, and show all products with all details.
    """
    model = ItemService
    template_name = 'stock/new-item-stock-list.html'
    paginate_by = 50
    page_kwarg = 'page'

    def querystring(self):
        qs = self.request.GET.copy()
        qs.pop(self.page_kwarg, None)
        return qs.urlencode()

    def get_queryset(self):
        search_txt = self.request.GET.get('q', '')
        return super().get_queryset().filter(name__icontains=search_txt).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stocks = self.get_queryset()
        query = self.querystring()

        paginator = Paginator(stocks, self.paginate_by)
        page_number = self.request.GET.get(self.page_kwarg, 1)
        stocks = paginator.get_page(page_number)

        context.update({
            'page_obj': stocks,
            'query': query,
            'item_form': ItemsForm(),
            'service_form': ServiceForm(),
        })
        return context

    def post(self, request):
        item_form = ItemsForm(request.POST)
        service_form = ServiceForm(request.POST)

        if item_form.is_valid():
            item_form.save(commit=False)
            item_form.instance.item_type = True
            item_form.save()
            messages.success(request, 'New Item saved successfully!')
            return HttpResponseRedirect(request.path_info)

        elif service_form.is_valid():
            service_form.save(commit=False)
            service_form.instance.item_type = False
            service_form.save()
            messages.success(request, 'New Service saved successfully!')
            return HttpResponseRedirect(request.path_info)

        context = {
            'item_form': item_form,
            'service_form': service_form,
        }
        return render(request, self.template_name, context)


class ItemView(LoginRequiredMixin, View):
    """
    View and edit single item/service details
    """
    template_name = 'stock/update-item.html'

    def get(self, request, p_id):
        data = get_object_or_404(ItemService, id=p_id)
        form = ItemsForm(instance=data) if data.item_type else ServiceForm(instance=data)
        context = {'form': form, 'p_id': p_id}
        return render(request, self.template_name, context)

    def post(self, request, p_id):
        data = get_object_or_404(ItemService, id=p_id)
        form = ItemsForm(request.POST, instance=data) if data.item_type else ServiceForm(request.POST, instance=data)

        if form.is_valid():
            form.save()
            messages.success(request, 'Item/Service updated successfully!')
            return HttpResponseRedirect('/stock/')

        context = {'form': form, 'p_id': p_id}
        return render(request, self.template_name, context)


class InvoiceView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Create new invoice and show previous invoices
    """
    model = Sale
    template_name = 'invoice/invoice.html'
    form_class = InvoiceForm
    page_kwarg = 'page'
    paginate_by = 50

    def querystring(self):
        qs = self.request.GET.copy()
        qs.pop(self.page_kwarg, None)
        return qs.urlencode()

    def get_queryset(self):
        # Show all invoice with net total of each invoice
        from_date = self.request.GET.get('from-date', '')
        to_date = self.request.GET.get('to-date', '')
        search_party = self.request.GET.get('q', '')

        filters = Q()

        if from_date and to_date:
            filters &= Q(bill_date__range=[from_date, to_date])
        if search_party:
            filters &= Q(party__name__icontains=search_party)

        qs = Sale.objects.filter(filters).order_by('-bill_date')

        net_total = qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        return qs, net_total

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = self.querystring()
        invoices, net_total = self.get_queryset()

        paginator = Paginator(invoices, self.paginate_by)
        page_number = self.request.GET.get(self.page_kwarg, 1)
        invoices = paginator.get_page(page_number)

        context.update({
            'page_obj': invoices,
            'query': query,
            'net_total': net_total,
        })
        return context


class TransactionView(LoginRequiredMixin, View):
    """
    Create new invoice and show previous invoices
    """
    # Have Signal to Update 'total_amount' when related Transaction 'added/updated/deleted'

    model = Transaction
    template_name = 'invoice/transaction.html'

    def get(self, request, p_id):
        sale = get_object_or_404(Sale, id=p_id)
        transactions = Transaction.objects.filter(sales=p_id)

        context = {
            'data': sale,
            'transactions': transactions,
            'p_id': p_id,
        }

        if sale.amount_paid == 0:
            context.update({
                'item_form': TransactionItemForm(),
                'service_form': TransactionServiceForm(),
            })

        return render(request, self.template_name, context)

    def post(self, request, p_id):
        sale = get_object_or_404(Sale, id=p_id)
        item_form = TransactionItemForm(request.POST)
        service_form = TransactionServiceForm(request.POST)

        if item_form.is_valid():
            transaction = item_form.save(commit=False)
            transaction.sales = sale
            transaction.save()

            # Reduce quantity from stock
            ItemService.objects.filter(name=transaction.item).update(
                quantity=F('quantity') - transaction.quantity
            )
            return HttpResponseRedirect("/invoice/{}/".format(p_id))

        elif service_form.is_valid():
            transaction = service_form.save(commit=False)
            transaction.sales = sale
            transaction.price = service_form.cleaned_data.get('amount', 0)

            transaction.save()
            return HttpResponseRedirect("/invoice/{}/".format(p_id))

        context = {
            'item_form': item_form,
            'service_form': service_form,
            'p_id': p_id,
        }
        return render(request, self.template_name, context)


class PrintInvoiceView(LoginRequiredMixin, View):
    template_name = 'invoice/print-invoice.html'

    def get(self, request, p_id):
        # Get company profile
        company = get_object_or_404(Profile, id=1)

        # Get Invoice detail
        bill = get_object_or_404(Sale, id=p_id)

        # Get Invoice transactions
        transactions = Transaction.objects.filter(sales=p_id)

        # # Get Total before discount
        # total_before_discount = sum(transaction.original_amount for transaction in transactions)

        # # Get Total discount
        # total_discount = sum(transaction.discount_amount for transaction in transactions)

        context = {
            'company': company,
            'bill': bill,
            'transactions': transactions,
        }

        return render(request, self.template_name, context)


class InvoicePaymentView(LoginRequiredMixin, View):
    template_name = 'invoice/invoice_payment.html'

    def get(self, request, sale_id):
        sale = get_object_or_404(Sale, pk=sale_id)
        return render(request, self.template_name, {'sale': sale})

    def post(self, request, sale_id):
        sale = get_object_or_404(Sale, pk=sale_id)

        try:
            payment_amount = int(request.POST.get('payment_amount', 0))
        except ValueError:
            messages.error(request, "Invalid payment amount.")
            return redirect(sale.get_absolute_url())

        if payment_amount <= 0:
            messages.error(request, "Payment amount must be greater than zero.")
            return redirect(sale.get_absolute_url())

        if payment_amount > sale.total_amount:
            messages.error(request, "Payment should not more than total amount.")
            return redirect(sale.get_absolute_url())


        sale.amount_paid = payment_amount
        sale.remaining_balance = sale.total_amount - payment_amount
        sale.save()

        # Update balance amount for current party
        sale.party.balance_amount = F('balance_amount') + sale.remaining_balance
        sale.party.save(update_fields=['balance_amount'])

        messages.success(request, "Payment successfully received.")
        return redirect(sale.get_absolute_url())


@method_decorator(csrf_exempt, name='dispatch')
def delete_invoice_ajax(request):
    """
    Delete invoice
    """
    if request.method == 'GET':
        invoice_id = request.GET.get('invoice_id', '')
        # Check if there is any transaction for related invoice
        trans = Transaction.objects.filter(sales=invoice_id)
        if not trans.exists():
            get_object_or_404(Sale, id=invoice_id).delete()
            result = "success"
        else:
            result = "failed"
    return JsonResponse({'result': result})


@method_decorator(csrf_exempt, name='dispatch')
def delete_transaction_ajax(request):
    """
    Delete selected transaction
    """
    if request.method == 'GET':
        trans_id = request.GET.get('trans_id', '')
        transaction = get_object_or_404(Transaction, id=trans_id)

        # If the transaction is for an item, adjust the item's quantity
        if transaction.item_type:
            ItemService.objects.filter(name=transaction.item).update(
                quantity=F('quantity') + transaction.quantity
            )

        transaction.delete()
        result = "success"
    return JsonResponse({'result': result})


def get_item_ajax(request):
    """
    Delete item price and quantity
    """
    if request.method == 'GET':
        item_id = request.GET.get('item_id', '')
        item = get_object_or_404(ItemService, id=item_id)
        return JsonResponse({
            'price': item.price,
            'quantity': item.quantity,
            'discount': item.discount,
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
def delete_balance_payment_ajax(request):
    """
    Delete selected payment balance payment transaction
    """
    if request.method == 'GET':
        transaction_id = request.GET.get('transaction_id', '')
        transaction = get_object_or_404(PartyBalance, id=transaction_id)
        transaction.delete()
        result = "success"

    return JsonResponse({'result': result})

def error_500(request):
    """
    Show 500 error page
    """
    return render(request, 'common/error500.html')


def error_404(request, exception):
    """
    Show 404 error page
    """
    return render(request, 'common/error404.html')
