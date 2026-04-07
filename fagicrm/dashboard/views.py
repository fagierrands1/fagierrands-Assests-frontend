from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
from .models import DashboardMetrics, Notification, SystemAlert
from employees.models import Employee


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        employee = None
    
    # Get dashboard metrics
    sales_summary = DashboardMetrics.get_sales_summary(employee=employee)
    activity_summary = DashboardMetrics.get_activity_summary(employee=employee)
    upcoming_tasks = DashboardMetrics.get_upcoming_tasks(employee=employee)
    recent_customers = DashboardMetrics.get_recent_customers()
    recent_leads = DashboardMetrics.get_recent_leads()
    
    # Get KPI summary if employee exists
    kpi_summary = None
    if employee:
        kpi_summary = DashboardMetrics.get_kpi_summary(employee)
    
    # Get notifications
    all_notifications = request.user.notifications.filter(is_dismissed=False)
    notifications = all_notifications[:10]
    unread_count = all_notifications.filter(is_read=False).count()
    
    # Get system alerts
    system_alerts = SystemAlert.objects.filter(
        is_active=True,
        start_date__lte=timezone.now()
    )
    if not request.user.is_superuser:
        system_alerts = system_alerts.filter(
            models.Q(target_all_users=True) |
            models.Q(target_users=request.user) |
            models.Q(target_departments__employees=employee)
        ).distinct()
    
    context = {
        'employee': employee,
        'sales_summary': sales_summary,
        'activity_summary': activity_summary,
        'kpi_summary': kpi_summary,
        'upcoming_tasks': upcoming_tasks,
        'recent_customers': recent_customers,
        'recent_leads': recent_leads,
        'notifications': notifications,
        'unread_notifications_count': unread_count,
        'system_alerts': system_alerts,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def employee_kpi_view(request, employee_id=None):
    """Employee KPI detailed view"""
    if employee_id:
        try:
            employee = Employee.objects.get(id=employee_id)
            # Check if user has permission to view this employee's KPIs
            if not request.user.is_superuser and request.user.employee_profile != employee:
                if not (hasattr(request.user, 'employee_profile') and 
                       request.user.employee_profile.is_manager and 
                       employee in request.user.employee_profile.direct_reports.all()):
                    return redirect('dashboard:dashboard')
        except Employee.DoesNotExist:
            return redirect('dashboard:dashboard')
    else:
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return redirect('dashboard:dashboard')
    
    # Get KPI data for the last 6 months
    end_date = timezone.now().replace(day=1).date()
    months_data = []
    
    for i in range(6):
        month_date = end_date - timedelta(days=32*i)
        month_date = month_date.replace(day=1)
        kpi_data = DashboardMetrics.get_kpi_summary(employee, month_date)
        kpi_data['month'] = month_date
        months_data.append(kpi_data)
    
    months_data.reverse()  # Show oldest to newest
    
    # Get current month performance
    current_performance = employee.get_current_month_performance()
    
    context = {
        'employee': employee,
        'months_data': months_data,
        'current_performance': current_performance,
    }
    
    return render(request, 'dashboard/employee_kpi.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.mark_as_read()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'})


@login_required
@require_http_methods(["POST"])
def dismiss_notification(request, notification_id):
    """Dismiss a notification"""
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.is_dismissed = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'})


@login_required
def notifications_view(request):
    """View all notifications"""
    notifications = request.user.notifications.all()
    
    # Mark all as read when viewing the page
    unread_notifications = notifications.filter(is_read=False)
    for notification in unread_notifications:
        notification.mark_as_read()
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'dashboard/notifications.html', context)


@login_required
def team_performance_view(request):
    """Team performance overview (for managers)"""
    try:
        employee = request.user.employee_profile
        if not employee.is_manager:
            return redirect('dashboard:dashboard')
    except Employee.DoesNotExist:
        return redirect('dashboard:dashboard')
    
    # Get team members
    team_members = employee.direct_reports.filter(employment_status='active')
    
    # Get performance data for each team member
    team_performance = []
    current_month = timezone.now().replace(day=1).date()
    
    for member in team_members:
        performance_data = member.get_current_month_performance()
        kpi_data = DashboardMetrics.get_kpi_summary(member, current_month)
        
        team_performance.append({
            'employee': member,
            'performance': performance_data,
            'kpi': kpi_data,
        })
    
    # Sort by overall performance score
    team_performance.sort(key=lambda x: x['kpi']['overall_score'], reverse=True)
    
    context = {
        'employee': employee,
        'team_performance': team_performance,
        'current_month': current_month,
    }
    
    return render(request, 'dashboard/team_performance.html', context)


class CustomLoginView(auth_views.LoginView):
    """Custom login view that redirects to dashboard"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/dashboard/'
