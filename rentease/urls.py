from django.contrib import admin
from django.urls import path
from . import views
from rentease import api_views

urlpatterns = [
    #  Auth
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.adduser, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),

    #  Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    #  Property
    path('property/', views.property, name='property'),
    path('add-property/', views.add_property, name='add_property'),
    path('edit-property/', views.edit_property, name='edit_property'),
    
    #  Tenant
    path('tenant/', views.tenant, name='tenant'),
    path('add-tenant/', views.add_tenant, name="add_tenant"),
    path('update-tenant/', views.update_tenant, name="update_tenant"),
    path('delete-tenant/<int:id>/', views.delete_tenant, name="delete_tenant"),

    #  Payment
    path('payment/', views.payment, name='payment'),
    path('add-payment/', views.add_payment, name='add_payment'),
    path('tenant-history/<int:tenant_id>/', views.tenant_history, name='tenant_history'),

    # Agreement
    path('agreement/', views.agreement, name='agreement'),
    path("add-agreement/", views.add_agreement, name="add_agreement"),
    path("update-agreement/", views.update_agreement, name="update_agreement"),

    #  Admin
    path('admin/', admin.site.urls),

    #  APIs
    path('api/properties/', api_views.api_get_properties, name='api_properties'),
    path('api/tenants/', api_views.api_get_tenants, name='api_tenants'),
    path('api/payments/', api_views.api_get_payments, name='api_payments'),
    path('api/dashboard/', api_views.api_dashboard_analytics, name='api_dashboard'),
]