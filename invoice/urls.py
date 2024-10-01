from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from invoice import views

app_name = 'invoice'

urlpatterns = [
    # Core Views
    path('', views.index, name='index'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),

    # Party Views
    path('parties/', views.PartiesView.as_view(), name='parties'),
    path('party/<int:pk>/', views.SinglePartyView.as_view(), name='party_detail'),
    path('party/<int:pk>/payment/', views.PartyBalanceView.as_view(), name='party_balance_payment'),

    # Stock and Item Views
    path('stock/', views.StockView.as_view(), name='stock'),
    path('item/<int:p_id>/', views.ItemView.as_view(), name='item_detail'),

    # Invoice and Transaction Views
    path('invoice/', views.InvoiceView.as_view(), name='invoice_list'),
    path('invoice/<int:p_id>/', views.TransactionView.as_view(), name='transaction_detail'),
    path('invoice/<int:p_id>/print/', views.PrintInvoiceView.as_view(), name='print_invoice'),
    path('invoice/<int:sale_id>/payment/', views.InvoicePaymentView.as_view(), name='invoice_payment'),

    # AJAX Views
    path('delete_invoice_ajax/', views.delete_invoice_ajax, name='delete_invoice_ajax'),
    path('delete_transaction_ajax/', views.delete_transaction_ajax, name='delete_transaction_ajax'),
    path('get_item_ajax/', views.get_item_ajax, name='get_item_ajax'),
    path('delete_balance_payment_ajax/', views.delete_balance_payment_ajax, name='delete_balance_payment_ajax'),

    # Favicon Redirect
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'))),
]
