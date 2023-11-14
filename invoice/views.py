###############################################################################
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View, ListView
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum, F
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin

from invoice.models import Profile, Party, ItemService, Sale, Transaction
from invoice.forms import (PartyForm, ItemsForm, ServiceForm, InvoiceForm,
                           TransactionItemForm, TransactionServiceForm)


def index(request):
    return render(request, 'invoice/index.html')


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profile
    template_name = 'invoice/profile.html'
    fields = ['name', 'phone', 'address', 'reg_no']
    success_message = 'Company is updated successfully!'


class PartiesView(LoginRequiredMixin, ListView):
    """
    Add new party, and show all parties with all details.
    """
    model = Party
    paginate_by = 50
    template_name = 'invoice/parties.html'

    def querystring(self):
        qs = self.request.GET.copy()
        qs.pop(self.page_kwarg, None)
        return qs.urlencode()

    def get_queryset(self):
        # Show all transaction with total purchase for all parties
        qs = super().get_queryset().annotate(
            total_bill=Sum('sale__transaction__amount')
        )

        search_txt = self.request.GET.get('q', '')
        qs = qs.filter(name__icontains=search_txt)
        return qs.order_by('name')

    def get(self, request):
        context_dict = {}

        form = PartyForm()
        context_dict['form'] = form

        parties = self.get_queryset()
        query = self.querystring()

        paginator = Paginator(parties, self.paginate_by)
        page_number = request.GET.get('page', '')
        parties = paginator.get_page(page_number)

        context_dict['parties'] = parties
        context_dict['query'] = query

        return render(request, self.template_name, context=context_dict)

    def post(self, request):
        form = PartyForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Party is saved successfully!')
            return HttpResponseRedirect(request.path_info)

        return render(request, self.template_name, {'form': form})


class PartyView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    View and edit single party details
    """
    model = Party
    template_name = 'invoice/update-party.html'
    fields = ['name', 'phone', 'address']
    success_message = 'Party is updated successfully!'


class StockView(LoginRequiredMixin, ListView):
    """
    Add new product, and show all products with all details.
    """
    model = ItemService
    paginate_by = 50
    template_name = 'invoice/stock.html'

    def querystring(self):
        qs = self.request.GET.copy()
        qs.pop(self.page_kwarg, None)
        return qs.urlencode()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(name__icontains=self.request.GET.get('q', ''))
        return qs.order_by('name')

    def get(self, request):
        context_dict = {}

        item_form = ItemsForm()
        context_dict['item_form'] = item_form

        service_form = ServiceForm()
        context_dict['service_form'] = service_form

        stocks = self.get_queryset()
        query = self.querystring()

        paginator = Paginator(stocks, self.paginate_by)
        page_number = request.GET.get('page', '')
        stocks = paginator.get_page(page_number)

        context_dict['stocks'] = stocks
        context_dict['query'] = query

        return render(request, self.template_name, context=context_dict)

    def post(self, request):
        item_form = ItemsForm(request.POST)
        service_form = ServiceForm(request.POST)

        if item_form.is_valid():
            data = ItemService(
                name=item_form.cleaned_data['name'],
                item_type=True,
                quantity=item_form.cleaned_data['quantity'],
                price=item_form.cleaned_data['price']
            )
            data.save()

            messages.success(request, 'Item is saved successfully!')
            return HttpResponseRedirect(request.path_info)

        if service_form.is_valid():
            data = ItemService(
                name=item_form.cleaned_data['name'],
                item_type=False,
                quantity=0,
                price=item_form.cleaned_data['price']
            )
            data.save()
            messages.success(request, 'Service is saved successfully!')
            return HttpResponseRedirect(request.path_info)

        context_dict = {}
        context_dict['item_form'] = item_form
        context_dict['service_form'] = service_form
        return render(request, self.template_name, context=context_dict)


class ItemView(LoginRequiredMixin, View):
    """
    View and edit single item/service details
    """
    template_name = 'invoice/update-item.html'

    def get(self, request, p_id):
        data = get_object_or_404(ItemService, id=p_id)

        if data.item_type:
            form = ItemsForm(instance=data)
        else:
            form = ServiceForm(instance=data)

        context_dict = {}
        context_dict['form'] = form
        context_dict['p_id'] = p_id
        return render(request, self.template_name, context=context_dict)

    def post(self, request, p_id):
        data = get_object_or_404(ItemService, id=p_id)

        if data.item_type:
            form = ItemsForm(request.POST, instance=data)
        else:
            form = ServiceForm(request.POST, instance=data)

        if form.is_valid():
            data.name = form.cleaned_data['name']
            data.price = form.cleaned_data['price']

            if data.item_type:
                data.quantity = form.cleaned_data['quantity']
            else:
                data.quantity = 0
            data.save()

            messages.success(request, 'Item/Service is updated successfully!')
            return HttpResponseRedirect('/stock/')

        context_dict = {}
        context_dict['form'] = form
        context_dict['p_id'] = p_id
        return render(request, self.template_name, context=context_dict)


class InvoiceView(LoginRequiredMixin, ListView):
    """
    Create new invoice and show previous invoices
    """
    model = Sale
    paginate_by = 50
    template_name = 'invoice/invoice.html'

    def querystring(self):
        qs = self.request.GET.copy()
        qs.pop(self.page_kwarg, None)
        return qs.urlencode()

    def get_queryset(self):
        # Show all invoice with net total of each invoice
        qs = super().get_queryset().annotate(
            net_total=Sum('transaction__amount')
        )

        from_date = self.request.GET.get('from-date', '')
        to_date = self.request.GET.get('to-date', '')
        search_party = self.request.GET.get('q', '')

        if from_date and to_date:
            qs = qs.filter(bill_date__range=[from_date, to_date])
        elif search_party:
            qs = qs.filter(party__name__icontains=search_party)

        if qs:
            net_total = qs.aggregate(Sum('net_total'))
        else:
            net_total = 0

        return (qs.order_by('-bill_date'), net_total)

    def get(self, request):
        context_dict = {}

        form = InvoiceForm()
        context_dict['form'] = form

        invoices, net_total = self.get_queryset()
        query = self.querystring()

        paginator = Paginator(invoices, self.paginate_by)
        page_number = request.GET.get('page', '')
        invoices = paginator.get_page(page_number)

        context_dict['invoices'] = invoices
        context_dict['query'] = query
        context_dict['net_total'] = net_total

        return render(request, self.template_name, context=context_dict)

    def post(self, request):
        form = InvoiceForm(request.POST)

        if form.is_valid():
            tmp = form.save(commit=True)
            return HttpResponseRedirect(f"/invoice/{str(tmp.id)}/")

        return render(request, self.template_name, {'form': form})


class TransactionView(LoginRequiredMixin, View):
    """
    Create new invoice and show previous invoices
    """
    model = Transaction
    template_name = 'invoice/transaction.html'

    def get(self, request, p_id):
        context_dict = {}

        data = get_object_or_404(Sale, id=p_id)
        context_dict['data'] = data

        item_form = TransactionItemForm()
        service_form = TransactionServiceForm()
        context_dict['item_form'] = item_form
        context_dict['service_form'] = service_form

        context_dict['p_id'] = p_id

        transactions = Transaction.objects.filter(sales=p_id)
        net_total = transactions.aggregate(Sum('amount'))
        context_dict['transactions'] = transactions
        context_dict['net_total'] = net_total

        return render(request, self.template_name, context=context_dict)

    def post(self, request, p_id):
        context_dict = {}

        data = get_object_or_404(Sale, id=p_id)

        item_form = TransactionItemForm(request.POST)
        service_form = TransactionServiceForm(request.POST)
        context_dict['item_form'] = item_form
        context_dict['service_form'] = service_form
        context_dict['p_id'] = p_id

        if item_form.is_valid():
            tmp_item = Transaction(
                sales=data,
                item=item_form.cleaned_data['item'],
                price=item_form.cleaned_data['price'],
                quantity=item_form.cleaned_data['quantity'],
                amount=item_form.cleaned_data['amount']
            )
            tmp_item.save()

            # Reduce quantity from stock
            ItemService.objects.filter(name=tmp_item.item).update(
                quantity=F('quantity')-tmp_item.quantity)

            return HttpResponseRedirect(f"/invoice/{str(p_id)}/")

        if service_form.is_valid():
            tmp_item = Transaction(
                sales=data,
                item=service_form.cleaned_data['item'],
                price=item_form.cleaned_data['amount'],
                amount=service_form.cleaned_data['amount']
            )
            tmp_item.save()

            return HttpResponseRedirect(f"/invoice/{str(p_id)}/")

        return render(request, self.template_name, context=context_dict)


class PrintInvoiceView(LoginRequiredMixin, View):
    template_name = 'invoice/print-invoice.html'

    def get(self, request, p_id):
        context_dict = {}

        # Get company profile
        company = get_object_or_404(Profile, id=1)
        context_dict['company'] = company

        # Get Invoice detail
        bill = get_object_or_404(Sale, id=p_id)
        context_dict['bill'] = bill

        # Get Invoice transactions
        transactions = Transaction.objects.filter(sales=p_id)
        context_dict['transactions'] = transactions

        # Get Total
        net_total = transactions.aggregate(Sum('amount'))
        context_dict['net_total'] = net_total

        return render(request, self.template_name, context=context_dict)


def delete_invoice_ajax(request):
    """
    Delete invoice
    """
    if request.method == 'GET':
        invoice_id = request.GET.get('invoice_id', '')
        # Check if there is any transaction for related invoice
        trans = Transaction.objects.filter(sales=invoice_id)
        if not trans:
            data = get_object_or_404(Sale, id=invoice_id)
            data.delete()
            result = "success"
        else:
            result = "failed"
    return JsonResponse({'result': result})


def delete_transaction_ajax(request):
    """
    Delete transaction
    """
    if request.method == 'GET':
        trans_id = request.GET.get('trans_id', '')
        data = get_object_or_404(Transaction, id=trans_id)

        # Check if data is item, if yes then increase its quantity
        if data.item_type:
            ItemService.objects.filter(
                name=data.item).update(quantity=F('quantity')+data.quantity)

        data.delete()
        result = "success"
    return JsonResponse({'result': result})


def get_item_ajax(request):
    """
    Delete item price and quantity
    """
    if request.method == 'GET':
        item_id = request.GET.get('item_id', '')
        data = get_object_or_404(ItemService, id=item_id)
    return JsonResponse({'price': data.price, 'quantity': data.quantity})


class UserView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'invoice/admin/user.html')


def error_500(request):
    return render(request, 'invoice/error500.html')


def error_404(request, exception):
    return render(request, 'invoice/error404.html')
