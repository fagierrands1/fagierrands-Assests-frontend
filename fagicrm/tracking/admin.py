from django.contrib import admin
from .models import DailyActivity, TimeEntry, Task, PerformanceMetric, ActivityLog


@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'total_hours_worked', 'calls_made', 'emails_sent', 'meetings_held', 'revenue_generated', 'productivity_score']
    list_filter = ['date', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['total_hours_worked', 'productivity_score', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'date')
        }),
        ('Time Tracking', {
            'fields': ('clock_in_time', 'clock_out_time', 'break_duration_minutes', 'total_hours_worked')
        }),
        ('Sales Activities', {
            'fields': ('calls_made', 'emails_sent', 'meetings_held', 'leads_contacted', 'demos_given', 'deals_closed')
        }),
        ('Customer Interactions', {
            'fields': ('customer_calls', 'customer_emails', 'customer_meetings', 'follow_ups_completed')
        }),
        ('Task Management', {
            'fields': ('tasks_assigned', 'tasks_completed', 'tasks_overdue')
        }),
        ('Service Requests', {
            'fields': ('service_requests_handled', 'service_requests_completed')
        }),
        ('Revenue', {
            'fields': ('revenue_generated',)
        }),
        ('Notes', {
            'fields': ('daily_notes', 'challenges_faced', 'achievements')
        }),
        ('Performance', {
            'fields': ('productivity_score',),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'activity_type', 'start_time', 'end_time', 'duration_minutes', 'is_billable']
    list_filter = ['activity_type', 'is_billable', 'date', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'description']
    readonly_fields = ['duration_minutes', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'date', 'activity_type', 'description')
        }),
        ('Time Details', {
            'fields': ('start_time', 'end_time', 'duration_minutes', 'is_billable')
        }),
        ('Related Objects', {
            'fields': ('customer', 'lead', 'service_request'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'status', 'priority', 'due_date', 'progress_percentage', 'is_overdue']
    list_filter = ['status', 'priority', 'assigned_to__department', 'due_date']
    search_fields = ['title', 'description', 'assigned_to__user__first_name', 'assigned_to__user__last_name']
    list_editable = ['status', 'priority', 'progress_percentage']
    readonly_fields = ['is_overdue', 'days_until_due', 'created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'assigned_to', 'assigned_by')
        }),
        ('Related Objects', {
            'fields': ('customer', 'lead', 'service_request'),
            'classes': ['collapse']
        }),
        ('Task Details', {
            'fields': ('status', 'priority', 'progress_percentage')
        }),
        ('Timeline', {
            'fields': ('due_date', 'started_at', 'completed_at', 'is_overdue', 'days_until_due')
        }),
        ('Time Estimation', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Notes', {
            'fields': ('notes', 'completion_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    actions = ['mark_completed']
    
    def mark_completed(self, request, queryset):
        updated = 0
        for task in queryset:
            if task.status != 'completed':
                task.mark_completed()
                updated += 1
        self.message_user(request, f'{updated} tasks marked as completed.')
    mark_completed.short_description = "Mark selected tasks as completed"


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ['employee', 'metric_type', 'period_start', 'period_end', 'overall_performance_score', 'total_revenue', 'deals_closed']
    list_filter = ['metric_type', 'period_start', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['calculated_at']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'metric_type', 'period_start', 'period_end')
        }),
        ('Sales Metrics', {
            'fields': ('total_revenue', 'deals_closed', 'conversion_rate', 'average_deal_size')
        }),
        ('Activity Metrics', {
            'fields': ('total_calls', 'total_emails', 'total_meetings', 'total_tasks_completed')
        }),
        ('Time Metrics', {
            'fields': ('total_hours_worked', 'billable_hours', 'average_response_time_hours')
        }),
        ('Customer Metrics', {
            'fields': ('new_customers_acquired', 'customer_satisfaction_avg', 'service_requests_completed')
        }),
        ('Performance Scores', {
            'fields': ('productivity_score', 'quality_score', 'overall_performance_score')
        }),
        ('Target Achievement', {
            'fields': ('sales_target_achievement', 'activity_target_achievement')
        }),
        ('Metadata', {
            'fields': ('calculated_at',),
            'classes': ['collapse']
        })
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee', 'action_type', 'description_preview', 'timestamp']
    list_filter = ['action_type', 'timestamp', 'user']
    search_fields = ['user__username', 'employee__user__first_name', 'employee__user__last_name', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Who and When', {
            'fields': ('user', 'employee', 'timestamp')
        }),
        ('What', {
            'fields': ('action_type', 'description')
        }),
        ('Related Objects', {
            'fields': ('customer_id', 'lead_id', 'service_request_id', 'task_id'),
            'classes': ['collapse']
        }),
        ('Additional Data', {
            'fields': ('old_value', 'new_value', 'ip_address'),
            'classes': ['collapse']
        })
    )
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description Preview'
