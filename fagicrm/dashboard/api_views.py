from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DashboardMetrics, Notification
from employees.models import Employee


@login_required
@require_http_methods(["GET"])
def dashboard_metrics_api(request):
    """API endpoint for dashboard metrics"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        employee = None
    
    # Get time range from query params
    days = int(request.GET.get('days', 30))
    
    # Get metrics
    sales_summary = DashboardMetrics.get_sales_summary(employee=employee, days=days)
    activity_summary = DashboardMetrics.get_activity_summary(employee=employee, days=days)
    
    # Get KPI summary if employee exists
    kpi_summary = None
    if employee:
        kpi_summary = DashboardMetrics.get_kpi_summary(employee)
    
    return JsonResponse({
        'sales_summary': sales_summary,
        'activity_summary': activity_summary,
        'kpi_summary': kpi_summary,
        'employee': {
            'id': employee.id if employee else None,
            'name': employee.full_name if employee else None,
            'department': employee.department.name if employee and employee.department else None,
        } if employee else None
    })


@login_required
@require_http_methods(["GET"])
def notifications_api(request):
    """API endpoint for notifications"""
    all_notifications = request.user.notifications.filter(is_dismissed=False)
    notifications = all_notifications[:20]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'customer_id': notification.customer_id,
            'lead_id': notification.lead_id,
            'service_request_id': notification.service_request_id,
            'task_id': notification.task_id,
        })
    
    unread_count = all_notifications.filter(is_read=False).count()
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count,
        'total_count': all_notifications.count()
    })


@login_required
@require_http_methods(["GET"])
def employee_performance_api(request, employee_id):
    """API endpoint for employee performance data"""
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # Check permissions
        if not request.user.is_superuser and request.user.employee_profile != employee:
            if not (hasattr(request.user, 'employee_profile') and 
                   request.user.employee_profile.is_manager and 
                   employee in request.user.employee_profile.direct_reports.all()):
                return JsonResponse({'error': 'Permission denied'}, status=403)
        
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
    # Get performance data for the last 6 months
    end_date = timezone.now().replace(day=1).date()
    months_data = []
    
    for i in range(6):
        month_date = end_date - timedelta(days=32*i)
        month_date = month_date.replace(day=1)
        kpi_data = DashboardMetrics.get_kpi_summary(employee, month_date)
        kpi_data['month'] = month_date.isoformat()
        months_data.append(kpi_data)
    
    months_data.reverse()  # Show oldest to newest
    
    # Get current month performance
    current_performance = employee.get_current_month_performance()
    
    return JsonResponse({
        'employee': {
            'id': employee.id,
            'name': employee.full_name,
            'position': employee.position,
            'department': employee.department.name if employee.department else None,
            'employee_id': employee.employee_id,
        },
        'months_data': months_data,
        'current_performance': current_performance,
    })


@login_required
@require_http_methods(["GET"])
def team_performance_api(request):
    """API endpoint for team performance data"""
    try:
        employee = request.user.employee_profile
        if not employee.is_manager:
            return JsonResponse({'error': 'Access denied. Manager role required.'}, status=403)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee profile not found'}, status=404)
    
    # Get team members
    team_members = employee.direct_reports.filter(employment_status='active')
    
    # Get performance data for each team member
    team_performance = []
    current_month = timezone.now().replace(day=1).date()
    
    for member in team_members:
        performance_data = member.get_current_month_performance()
        kpi_data = DashboardMetrics.get_kpi_summary(member, current_month)
        
        team_performance.append({
            'employee': {
                'id': member.id,
                'name': member.full_name,
                'position': member.position,
                'employee_id': member.employee_id,
            },
            'performance': performance_data,
            'kpi': kpi_data,
        })
    
    # Sort by overall performance score
    team_performance.sort(key=lambda x: x['kpi']['overall_score'], reverse=True)
    
    return JsonResponse({
        'manager': {
            'id': employee.id,
            'name': employee.full_name,
            'department': employee.department.name if employee.department else None,
        },
        'team_performance': team_performance,
        'current_month': current_month.isoformat(),
        'team_size': len(team_performance),
    })


@login_required
@require_http_methods(["POST"])
def create_notification(request):
    """API endpoint to create notifications"""
    import json
    
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Get target users
        target_users = []
        if data.get('target_all_users'):
            from django.contrib.auth.models import User
            target_users = User.objects.filter(is_active=True)
        elif data.get('target_user_ids'):
            from django.contrib.auth.models import User
            target_users = User.objects.filter(id__in=data['target_user_ids'])
        elif data.get('target_department_ids'):
            from employees.models import Department
            departments = Department.objects.filter(id__in=data['target_department_ids'])
            target_users = []
            for dept in departments:
                target_users.extend(dept.employees.filter(employment_status='active'))
        
        # Create notifications
        created_count = 0
        for user in target_users:
            Notification.objects.create(
                user=user,
                notification_type=data.get('notification_type', 'info'),
                title=data['title'],
                message=data['message'],
                customer_id=data.get('customer_id'),
                lead_id=data.get('lead_id'),
                service_request_id=data.get('service_request_id'),
                task_id=data.get('task_id'),
            )
            created_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'Created {created_count} notifications',
            'created_count': created_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing required field: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)