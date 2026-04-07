from django.urls import path
from . import views, api_views

app_name = 'dashboard'

urlpatterns = [
    # Main views
    path('', views.dashboard_view, name='dashboard'),
    path('kpi/', views.employee_kpi_view, name='employee_kpi'),
    path('kpi/<int:employee_id>/', views.employee_kpi_view, name='employee_kpi_detail'),
    path('team/', views.team_performance_view, name='team_performance'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
    
    # API endpoints
    path('api/metrics/', api_views.dashboard_metrics_api, name='api_dashboard_metrics'),
    path('api/notifications/', api_views.notifications_api, name='api_notifications'),
    path('api/employee/<int:employee_id>/performance/', api_views.employee_performance_api, name='api_employee_performance'),
    path('api/team/performance/', api_views.team_performance_api, name='api_team_performance'),
    path('api/notifications/create/', api_views.create_notification, name='api_create_notification'),
]