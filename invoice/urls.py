from django.urls import path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from invoice import views

app_name = 'invoice'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:pk>/', views.ProfileView.as_view(), name='profile'),
    path('parties/', views.PartiesView.as_view(), name='parties'),
    path('party/<int:pk>/', views.PartyView.as_view(), name='party'),
    path('stock/', views.StockView.as_view(), name='stock'),
    path('item/<int:p_id>/', views.ItemView.as_view(), name='item'),
    path('invoice/', views.InvoiceView.as_view(), name='invoice'),
    path('invoice/<int:p_id>/', views.TransactionView.as_view(),
         name='transaction'),
    path('print-invoice/<int:p_id>/', views.PrintInvoiceView.as_view(),
         name='print-invoice'),

    path('delete_invoice_ajax/', views.delete_invoice_ajax,
         name='delete_invoice_ajax'),
    path('delete_transaction_ajax/', views.delete_transaction_ajax,
         name='delete_transaction_ajax'),
    path('get_item_ajax/', views.get_item_ajax, name='get_item_ajax'),

    path('favicon.ico', RedirectView.as_view(
        url=staticfiles_storage.url('images/favicon.ico'))),
]
