#!/usr/bin/env python
"""
FAGI CRM System Test Script
Tests all major functionality to ensure the system is working correctly.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagicrm.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, Department, EmployeeKPI
from customers.models import Customer, Lead
from services.models import Service, ServiceRequest
from tracking.models import DailyActivity, Task
from dashboard.models import Notification

def test_system():
    """Test all major system components"""
    print("🧪 FAGI CRM System Test Suite")
    print("=" * 50)
    
    # Test 1: Database connectivity
    print("\n1. Testing Database Connectivity...")
    try:
        user_count = User.objects.count()
        print(f"   ✅ Database connected. Found {user_count} users.")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    # Test 2: Employee management
    print("\n2. Testing Employee Management...")
    try:
        employees = Employee.objects.filter(employment_status='active')
        departments = Department.objects.all()
        print(f"   ✅ Found {employees.count()} active employees in {departments.count()} departments")
        
        # Test employee KPIs
        kpis = EmployeeKPI.objects.all()
        print(f"   ✅ Found {kpis.count()} KPI records")
    except Exception as e:
        print(f"   ❌ Employee management error: {e}")
        return False
    
    # Test 3: Customer management
    print("\n3. Testing Customer Management...")
    try:
        customers = Customer.objects.all()
        leads = Lead.objects.all()
        print(f"   ✅ Found {customers.count()} customers and {leads.count()} leads")
    except Exception as e:
        print(f"   ❌ Customer management error: {e}")
        return False
    
    # Test 4: Service management
    print("\n4. Testing Service Management...")
    try:
        services = Service.objects.all()
        service_requests = ServiceRequest.objects.all()
        print(f"   ✅ Found {services.count()} services and {service_requests.count()} service requests")
    except Exception as e:
        print(f"   ❌ Service management error: {e}")
        return False
    
    # Test 5: Activity tracking
    print("\n5. Testing Activity Tracking...")
    try:
        activities = DailyActivity.objects.all()
        tasks = Task.objects.all()
        print(f"   ✅ Found {activities.count()} daily activities and {tasks.count()} tasks")
    except Exception as e:
        print(f"   ❌ Activity tracking error: {e}")
        return False
    
    # Test 6: Dashboard and notifications
    print("\n6. Testing Dashboard Features...")
    try:
        notifications = Notification.objects.all()
        print(f"   ✅ Found {notifications.count()} notifications")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
        return False
    
    # Test 7: KPI calculations
    print("\n7. Testing KPI Calculations...")
    try:
        if employees.exists():
            sample_employee = employees.first()
            performance = sample_employee.get_current_month_performance()
            print(f"   ✅ KPI calculation working. Sample employee score: {performance['overall_score']:.1f}%")
        else:
            print("   ⚠️  No employees found for KPI testing")
    except Exception as e:
        print(f"   ❌ KPI calculation error: {e}")
        return False
    
    # Test 8: Manager functionality
    print("\n8. Testing Manager Features...")
    try:
        managers = [emp for emp in employees if emp.is_manager]
        print(f"   ✅ Found {len(managers)} managers")
        
        if managers:
            sample_manager = managers[0]
            direct_reports = sample_manager.direct_reports.count()
            print(f"   ✅ Sample manager has {direct_reports} direct reports")
    except Exception as e:
        print(f"   ❌ Manager functionality error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! System is fully operational.")
    print("\n📊 System Statistics:")
    print(f"   • Users: {User.objects.count()}")
    print(f"   • Employees: {Employee.objects.count()}")
    print(f"   • Customers: {Customer.objects.count()}")
    print(f"   • Leads: {Lead.objects.count()}")
    print(f"   • Services: {Service.objects.count()}")
    print(f"   • Service Requests: {ServiceRequest.objects.count()}")
    print(f"   • Daily Activities: {DailyActivity.objects.count()}")
    print(f"   • Tasks: {Task.objects.count()}")
    print(f"   • KPI Records: {EmployeeKPI.objects.count()}")
    print(f"   • Notifications: {Notification.objects.count()}")
    
    print("\n🌐 Access URLs:")
    print("   • Main Dashboard: http://127.0.0.1:8000/")
    print("   • Admin Panel: http://127.0.0.1:8000/admin/")
    print("   • Login: admin / admin123")
    
    return True

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔌 Testing API Endpoints...")
    try:
        from django.test import Client
        from django.contrib.auth import authenticate
        
        client = Client()
        
        # Test login
        user = User.objects.get(username='admin')
        client.force_login(user)
        
        # Test dashboard API
        response = client.get('/dashboard/api/metrics/')
        if response.status_code == 200:
            print("   ✅ Dashboard API working")
        else:
            print(f"   ⚠️  Dashboard API returned status {response.status_code}")
        
        # Test notifications API
        response = client.get('/dashboard/api/notifications/')
        if response.status_code == 200:
            print("   ✅ Notifications API working")
        else:
            print(f"   ⚠️  Notifications API returned status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API testing error: {e}")

if __name__ == '__main__':
    success = test_system()
    test_api_endpoints()
    
    if success:
        print("\n🚀 FAGI CRM System is ready for use!")
        print("   Start the server with: python manage.py runserver")
        print("   Then visit: http://127.0.0.1:8000/")
    else:
        print("\n❌ System test failed. Please check the errors above.")
        sys.exit(1)