from django.contrib import admin
from django.utils import timezone
from .models import DashboardWidget, Notification, SystemAlert


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'widget_type', 'title', 'is_visible', 'position_x', 'position_y', 'width', 'height']
    list_filter = ['widget_type', 'is_visible', 'created_at']
    search_fields = ['user__username', 'title']
    list_editable = ['is_visible']
    
    fieldsets = (
        ('Widget Information', {
            'fields': ('user', 'widget_type', 'title')
        }),
        ('Position and Size', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('Settings', {
            'fields': ('is_visible', 'settings')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'is_dismissed', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_dismissed', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_editable = ['is_read', 'is_dismissed']
    readonly_fields = ['read_at', 'created_at']
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('customer_id', 'lead_id', 'service_request_id', 'task_id'),
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ('is_read', 'is_dismissed', 'read_at')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ['collapse']
        })
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(SystemAlert)
class SystemAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'is_active', 'target_all_users', 'start_date', 'end_date', 'is_current']
    list_filter = ['alert_type', 'is_active', 'target_all_users', 'start_date']
    search_fields = ['title', 'message']
    list_editable = ['is_active']
    readonly_fields = ['is_current', 'created_at']
    filter_horizontal = ['target_departments', 'target_users']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'title', 'message')
        }),
        ('Targeting', {
            'fields': ('target_all_users', 'target_departments', 'target_users')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Status', {
            'fields': ('is_active', 'is_dismissible')
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by'),
            'classes': ['collapse']
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
