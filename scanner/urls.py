from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_and_scan, name='upload_scan'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Document Actions (All need <int:doc_id>)
    path('download/<int:doc_id>/', views.download_pdf, name='download_pdf'),
    path('pay/<int:doc_id>/', views.pay_for_scan, name='pay_for_scan'),
    path('check-status/<int:doc_id>/', views.check_payment_status, name='check_payment_status'),
    
    # Static Actions
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('contact/', views.contact_view, name='contact'),
]