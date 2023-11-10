from django.urls import path
from invoice import views

app_name = 'invoice'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('parties/', views.PartiesView.as_view(), name='parties'),
    path('party/<int:p_id>/', views.PartyView.as_view(), name='party'),
    path('stock/', views.StockView.as_view(), name='stock'),
    path('item/<int:p_id>/', views.ItemView.as_view(), name='item'),
    path('invoice/', views.InvoiceView.as_view(), name='invoice'),
    path('invoice/<int:p_id>/', views.TransactionView.as_view(),
         name='transaction'),
    path('print-invoice/<int:p_id>/', views.print_invoice,
         name='print-invoice'),

    path('delete_invoice_ajax/', views.delete_invoice_ajax,
         name='delete_invoice_ajax'),
    path('delete_transaction_ajax/', views.delete_transaction_ajax,
         name='delete_transaction_ajax'),
    path('get_item_ajax/', views.get_item_ajax, name='get_item_ajax'),
]
