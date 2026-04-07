from django.contrib import admin
from .models import Customer, Lead, CustomerNote, LeadNote


class CustomerNoteInline(admin.TabularInline):
    model = CustomerNote
    extra = 1
    fields = ['note', 'is_important', 'created_by']
    readonly_fields = ['created_by']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company_name', 'email', 'phone', 'status', 'assigned_employee', 'total_spent', 'created_at']
    list_filter = ['status', 'customer_type', 'assigned_employee', 'created_at', 'preferred_contact_method']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'phone']
    list_editable = ['status', 'assigned_employee']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'company_name', 'customer_type')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'alternate_phone', 'preferred_contact_method')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Business Information', {
            'fields': ('status', 'assigned_employee', 'total_spent', 'lifetime_value')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ['collapse']
        })
    )
    
    inlines = [CustomerNoteInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new customer
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class LeadNoteInline(admin.TabularInline):
    model = LeadNote
    extra = 1
    fields = ['note', 'is_important', 'created_by']
    readonly_fields = ['created_by']


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company_name', 'email', 'phone', 'status', 'source', 'assigned_employee', 'estimated_value', 'created_at']
    list_filter = ['status', 'source', 'urgency', 'assigned_employee', 'created_at']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'phone']
    list_editable = ['status', 'assigned_employee']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'converted_to_customer', 'conversion_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'company_name', 'title')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Lead Information', {
            'fields': ('status', 'source', 'assigned_employee', 'urgency')
        }),
        ('Service Interest', {
            'fields': ('interested_services', 'estimated_value')
        }),
        ('Conversion', {
            'fields': ('converted_to_customer', 'conversion_date'),
            'classes': ['collapse']
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ['collapse']
        })
    )
    
    inlines = [LeadNoteInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new lead
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['convert_to_customer']
    
    def convert_to_customer(self, request, queryset):
        converted_count = 0
        for lead in queryset:
            if not lead.converted_to_customer:
                lead.convert_to_customer(request.user)
                converted_count += 1
        
        self.message_user(request, f'{converted_count} leads converted to customers.')
    convert_to_customer.short_description = "Convert selected leads to customers"


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ['customer', 'note_preview', 'is_important', 'created_by', 'created_at']
    list_filter = ['is_important', 'created_at', 'created_by']
    search_fields = ['customer__first_name', 'customer__last_name', 'note']
    readonly_fields = ['created_at']
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note Preview'


@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ['lead', 'note_preview', 'is_important', 'created_by', 'created_at']
    list_filter = ['is_important', 'created_at', 'created_by']
    search_fields = ['lead__first_name', 'lead__last_name', 'note']
    readonly_fields = ['created_at']
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note Preview'
