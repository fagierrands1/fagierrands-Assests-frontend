from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from employees.models import Employee, EmployeeKPI
from tracking.models import DailyActivity, Task, PerformanceMetric
from services.models import ServiceRequest
from customers.models import Lead, Customer


class Command(BaseCommand):
    help = 'Calculate and update KPIs for all employees'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Month to calculate KPIs for (YYYY-MM format). Defaults to current month.',
        )
        parser.add_argument(
            '--employee-id',
            type=int,
            help='Calculate KPIs for specific employee only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recalculation even if KPIs already exist',
        )

    def handle(self, *args, **options):
        # Determine the month to calculate
        if options['month']:
            try:
                year, month = options['month'].split('-')
                target_month = datetime(int(year), int(month), 1).date()
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid month format. Use YYYY-MM'))
                return
        else:
            target_month = timezone.now().replace(day=1).date()

        self.stdout.write(f'Calculating KPIs for {target_month.strftime("%B %Y")}...')

        # Get employees to process
        if options['employee_id']:
            try:
                employees = [Employee.objects.get(id=options['employee_id'])]
            except Employee.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Employee with ID {options["employee_id"]} not found'))
                return
        else:
            employees = Employee.objects.filter(employment_status='active')

        processed_count = 0
        updated_count = 0
        created_count = 0

        for employee in employees:
            try:
                # Check if KPI already exists
                kpi, created = EmployeeKPI.objects.get_or_create(
                    employee=employee,
                    month=target_month,
                    defaults={'calculated_at': timezone.now()}
                )

                if not created and not options['force']:
                    self.stdout.write(f'KPI for {employee.full_name} already exists. Use --force to recalculate.')
                    continue

                # Calculate KPIs
                kpi_data = self.calculate_employee_kpis(employee, target_month)
                
                # Update KPI object
                for field, value in kpi_data.items():
                    setattr(kpi, field, value)
                
                kpi.calculated_at = timezone.now()
                kpi.save()

                if created:
                    created_count += 1
                    self.stdout.write(f'Created KPI for {employee.full_name}')
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated KPI for {employee.full_name}')

                processed_count += 1

            except Exception as e:
                import traceback
                self.stdout.write(
                    self.style.ERROR(f'Error processing {employee.full_name}: {str(e)}')
                )
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write(
            self.style.SUCCESS(
                f'KPI calculation completed:\n'
                f'- Processed: {processed_count} employees\n'
                f'- Created: {created_count} new KPIs\n'
                f'- Updated: {updated_count} existing KPIs'
            )
        )

    def calculate_employee_kpis(self, employee, target_month):
        """Calculate KPIs for a specific employee and month"""
        # Calculate date range for the month
        month_start = target_month
        if target_month.month == 12:
            month_end = target_month.replace(year=target_month.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = target_month.replace(month=target_month.month + 1) - timedelta(days=1)

        # Get daily activities for the month
        activities = DailyActivity.objects.filter(
            employee=employee,
            date__gte=month_start,
            date__lte=month_end
        )

        # Get service requests for the month
        service_requests = ServiceRequest.objects.filter(
            assigned_employee=employee,
            created_at__gte=timezone.make_aware(datetime.combine(month_start, datetime.min.time())),
            created_at__lte=timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        )

        # Get leads for the month
        leads = Lead.objects.filter(
            assigned_employee=employee,
            created_at__gte=timezone.make_aware(datetime.combine(month_start, datetime.min.time())),
            created_at__lte=timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        )

        # Get tasks for the month
        tasks = Task.objects.filter(
            assigned_to=employee,
            created_at__gte=timezone.make_aware(datetime.combine(month_start, datetime.min.time())),
            created_at__lte=timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        )

        # Calculate revenue metrics
        completed_requests = service_requests.filter(status='completed')
        revenue_generated = sum(float(sr.total_amount) for sr in completed_requests if sr.total_amount)
        deals_closed = completed_requests.count()

        # Calculate conversion metrics
        total_leads = leads.count()
        won_leads = leads.filter(status='won').count()
        conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0

        # Calculate activity metrics
        total_calls = sum(activity.calls_made for activity in activities)
        total_emails = sum(activity.emails_sent for activity in activities)
        total_meetings = sum(activity.meetings_held for activity in activities)
        total_hours_worked = sum(float(activity.total_hours_worked) for activity in activities)

        # Calculate task metrics
        completed_tasks = tasks.filter(status='completed').count()
        total_tasks = tasks.count()

        # Calculate customer metrics
        new_customers = Customer.objects.filter(
            assigned_employee=employee,
            created_at__gte=timezone.make_aware(datetime.combine(month_start, datetime.min.time())),
            created_at__lte=timezone.make_aware(datetime.combine(month_end, datetime.max.time()))
        ).count()

        # Calculate average deal size
        average_deal_size = revenue_generated / deals_closed if deals_closed > 0 else 0

        # Calculate billable hours (assuming all service request hours are billable)
        billable_hours_total = 0
        for sr in completed_requests:
            if sr.service and sr.service.estimated_duration_minutes:
                billable_hours_total += sr.service.estimated_duration_minutes / 60
        billable_hours = billable_hours_total

        # Calculate average response time (simplified - using a default value)
        average_response_time_hours = 2.5  # This would need more complex calculation

        # Calculate customer satisfaction (simplified - using random value for demo)
        import random
        customer_satisfaction_avg = random.uniform(3.5, 5.0)

        # Calculate service completion rate
        total_service_requests = service_requests.count()
        service_completion_rate = (deals_closed / total_service_requests * 100) if total_service_requests > 0 else 0

        # Calculate target achievements
        sales_target_achievement = (revenue_generated / float(employee.monthly_sales_target) * 100) if employee.monthly_sales_target > 0 else 0
        
        # Activity target achievement (weighted average)
        calls_achievement = (total_calls / employee.monthly_calls_target * 100) if employee.monthly_calls_target > 0 else 0
        meetings_achievement = (total_meetings / employee.monthly_meetings_target * 100) if employee.monthly_meetings_target > 0 else 0
        activity_target_achievement = (calls_achievement + meetings_achievement) / 2

        # Calculate performance scores
        productivity_score = min(100, (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        quality_score = min(100, customer_satisfaction_avg * 20)  # Convert 5-point scale to 100-point scale

        # Calculate overall performance score (weighted average)
        overall_performance_score = (
            sales_target_achievement * 0.4 +
            activity_target_achievement * 0.3 +
            productivity_score * 0.2 +
            quality_score * 0.1
        )

        return {
            'revenue_generated': Decimal(str(revenue_generated)),
            'deals_closed': deals_closed,
            'conversion_rate': Decimal(str(conversion_rate)),
            'average_deal_size': Decimal(str(average_deal_size)),
            'total_calls': total_calls,
            'total_emails': total_emails,
            'total_meetings': total_meetings,
            'total_tasks_completed': completed_tasks,
            'total_hours_worked': Decimal(str(total_hours_worked)),
            'billable_hours': Decimal(str(billable_hours)),
            'average_response_time_hours': Decimal(str(average_response_time_hours)),
            'new_customers_acquired': new_customers,
            'customer_satisfaction_avg': Decimal(str(customer_satisfaction_avg)),
            'customer_retention_rate': Decimal('90.0'),  # Simplified
            'service_completion_rate': Decimal(str(service_completion_rate)),
            'sales_target_achievement': Decimal(str(sales_target_achievement)),
            'activity_target_achievement': Decimal(str(activity_target_achievement)),
            'productivity_score': Decimal(str(productivity_score)),
            'quality_score': Decimal(str(quality_score)),
            'overall_performance_score': Decimal(str(overall_performance_score)),
        }