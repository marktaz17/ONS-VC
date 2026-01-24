from django.urls import path
from . import views

urlpatterns = [
path('login_page/', views.login_page, name='login_page'),
path('', views.home, name='home'),
path('logout/', views.user_logout, name='logout'),
# path('details/<int:pk>', views.details, name='details'),
path('delete/<int:pk>', views.delete_record, name='delete'),
path('add/', views.add_record, name='add'),
path('update/<int:pk>', views.update_record, name='update'),

path('holiday_table/', views.holiday_table, name='holiday_table'),
path('add_holiday/', views.add_holiday, name='add_holiday'),
path('delete_holiday/<int:pk>', views.delete_holiday, name='delete_holiday'),

path('signatory_table/', views.signatory_table, name='signatory_table'),
path('add_signatory/', views.add_signatory, name='add_signatory'),
path('delete_signatory/<int:pk>', views.delete_signatory, name='delete_signatory'),

path('notice/', views.notice, name='notice'),
path('print_notice/<int:pk>', views.print_notice, name='print_notice'),
path('update_signatory/<int:pk>', views.update_signatory, name='update_signatory'),
path('print_all_notice/', views.print_all_notice, name='print_all_notice'),
# path('download_all_pdf/', views.download_all_pdf, name='download_all_pdf'),
# path('download_pdf/', views.generatepdf, name='download_pdf'),
path('dashboard/', views.dashboard, name='dashboard'),
path('dashboard/data/', views.dashboard_data, name='dashboard_data'),  # Add this line
path('reprint_notice/', views.reprint_notice, name='reprint_notice'),
path('reprint_notice_id/<int:pk>', views.reprint_notice_id, name='reprint_notice_id'),
path('reports/', views.reports, name='reports'),
path('print_report/', views.print_report, name='print_report'),

path ('daily_encoded_report/', views.daily_encoded_report, name='daily_encoded_report'),
path ('print_encoded_report/', views.print_encoded_report, name='print_encoded_report'),

path ('occupancy_and_electrical_payments', views.occupancy_and_electrical_payments, name='occupancy_and_electrical_payments'),
path ('print_occupancy_and_electrical_payments', views.print_occupancy_and_electrical_payments, name='print_occupancy_and_electrical_payments'),

path('print_history/', views.print_history, name='print_history'),
path('modal_open', views.modal_open, name='modal_open'),
# path('check-session/', views.check_session_data, name='check_session'),
path('print_backside', views.print_backside, name='print_backside'),
path('pending_notice', views.pending_notice, name='pending_notice'),
path('print_pending_notice/<int:pk>', views.print_pending_notice, name='print_pending_notice'),
path('database_table', views.database_table, name='database_table'),
path('update_database_table/<int:pk>', views.update_database_table, name='update_database_table'),
path('audit_trail/', views.audit_trail, name='audit_trail'),

]