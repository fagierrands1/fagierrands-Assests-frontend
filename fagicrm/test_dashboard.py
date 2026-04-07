#!/usr/bin/env python
"""
Test the dashboard view directly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagicrm.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_dashboard():
    """Test dashboard view"""
    print("🧪 Testing Dashboard View...")
    
    try:
        # Create test client
        client = Client()
        
        # Get admin user
        admin_user = User.objects.get(username='admin')
        
        # Login as admin
        client.force_login(admin_user)
        
        # Test dashboard view
        response = client.get('/dashboard/')
        
        if response.status_code == 200:
            print("   ✅ Dashboard view working correctly")
            print(f"   ✅ Response status: {response.status_code}")
            print("   ✅ Dashboard loaded successfully")
            return True
        else:
            print(f"   ❌ Dashboard returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Dashboard test failed: {str(e)}")
        return False

def test_other_views():
    """Test other dashboard views"""
    print("\n🧪 Testing Other Dashboard Views...")
    
    client = Client()
    admin_user = User.objects.get(username='admin')
    client.force_login(admin_user)
    
    views_to_test = [
        ('/dashboard/kpi/', 'Employee KPI'),
        ('/dashboard/notifications/', 'Notifications'),
        ('/dashboard/api/metrics/', 'Dashboard API'),
        ('/dashboard/api/notifications/', 'Notifications API'),
    ]
    
    for url, name in views_to_test:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"   ✅ {name} view working")
            else:
                print(f"   ⚠️  {name} returned status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name} failed: {str(e)}")

if __name__ == '__main__':
    success = test_dashboard()
    test_other_views()
    
    if success:
        print("\n🎉 Dashboard is working correctly!")
        print("   You can now access: http://127.0.0.1:8000/dashboard/")
        print("   Login with: admin / admin123")
    else:
        print("\n❌ Dashboard test failed")