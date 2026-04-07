from django.urls import path
from . import api_views

app_name = 'customers_api'

urlpatterns = [
    path('health/', api_views.health_check, name='health_check'),
    path('customers/', api_views.customers_api, name='customers_list'),
    path('customers/<int:customer_id>/', api_views.customer_detail_api, name='customer_detail'),
    path('employees/', api_views.employees_api, name='employees_list'),
    path('asset-assignments/', api_views.asset_assignments_api, name='asset_assignments'),
]