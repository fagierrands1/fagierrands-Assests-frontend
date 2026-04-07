from django.contrib import admin
from .models import Department, Employee, EmployeeKPI, EmployeeGoal


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'employee_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    
    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = 'Employee Count'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'employee_id', 'position', 'department', 'employment_status', 'hire_date', 'manager']
    list_filter = ['employment_status', 'employment_type', 'department', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'position']
    list_editable = ['employment_status', 'department']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Employee Information', {
            'fields': ('employee_id', 'position', 'department', 'manager')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Employment Details', {
            'fields': ('employment_status', 'employment_type', 'hire_date', 'termination_date')
        }),
        ('Compensation', {
            'fields': ('salary', 'hourly_rate', 'commission_rate')
        }),
        ('Performance Targets', {
            'fields': ('monthly_sales_target', 'monthly_calls_target', 'monthly_meetings_target')
        }),
        ('Profile', {
            'fields': ('bio', 'profile_picture')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'department', 'manager__user')


@admin.register(EmployeeKPI)
class EmployeeKPIAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'overall_score', 'revenue_generated', 'deals_closed', 'customer_satisfaction_score']
    list_filter = ['month', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['overall_score', 'created_at', 'updated_at']
    date_hierarchy = 'month'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'month')
        }),
        ('Sales Metrics', {
            'fields': ('revenue_generated', 'deals_closed', 'conversion_rate')
        }),
        ('Activity Metrics', {
            'fields': ('calls_made', 'emails_sent', 'meetings_held', 'tasks_completed')
        }),
        ('Customer Metrics', {
            'fields': ('new_customers_acquired', 'customer_satisfaction_score', 'customer_retention_rate')
        }),
        ('Productivity Metrics', {
            'fields': ('average_response_time_hours', 'service_completion_rate')
        }),
        ('Target Achievement', {
            'fields': ('sales_target_achievement', 'activity_target_achievement')
        }),
        ('Overall Performance', {
            'fields': ('overall_score',),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )


@admin.register(EmployeeGoal)
class EmployeeGoalAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'goal_type', 'progress_percentage', 'status', 'target_date', 'is_overdue']
    list_filter = ['goal_type', 'status', 'target_date', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'title']
    list_editable = ['status']
    readonly_fields = ['progress_percentage', 'is_overdue', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Goal Information', {
            'fields': ('employee', 'title', 'description', 'goal_type')
        }),
        ('Target and Progress', {
            'fields': ('target_value', 'current_value', 'unit', 'progress_percentage')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_date', 'completed_date')
        }),
        ('Status', {
            'fields': ('status', 'is_overdue')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ['collapse']
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
