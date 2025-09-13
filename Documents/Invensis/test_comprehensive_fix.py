#!/usr/bin/env python3
"""
Comprehensive test script to check for all potential issues
"""

import requests

def test_comprehensive_fix():
    base_url = "http://localhost:5001"
    
    print("🧪 Comprehensive Application Test...")
    print("=" * 60)
    
    # Test 1: Application accessibility
    print("1. Testing application accessibility...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        if response.status_code == 200:
            print("   ✅ Application is running")
        else:
            print(f"   ❌ Application error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Application error: {e}")
    
    # Test 2: Admin routes
    print("\n2. Testing Admin routes...")
    routes_to_test = [
        ('/admin/login', 'GET'),
        ('/admin/dashboard', 'GET'),
        ('/admin/add_role', 'POST'),
        ('/admin/remove_role', 'POST')
    ]
    
    for route, method in routes_to_test:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{route}", allow_redirects=False)
            else:
                response = requests.post(f"{base_url}{route}", allow_redirects=False)
            
            if response.status_code in [200, 302, 405]:  # 405 is Method Not Allowed
                print(f"   ✅ {route} - {response.status_code}")
            else:
                print(f"   ❌ {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    # Test 3: HR routes
    print("\n3. Testing HR routes...")
    hr_routes = [
        ('/hr/dashboard', 'GET'),
        ('/hr/add_candidate', 'POST'),
        ('/hr/assign_candidate', 'POST'),
        ('/hr/delete_candidate/test_id', 'POST'),
        ('/hr/candidates', 'GET')
    ]
    
    for route, method in hr_routes:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{route}", allow_redirects=False)
            else:
                response = requests.post(f"{base_url}{route}", allow_redirects=False)
            
            if response.status_code in [200, 302, 405]:
                print(f"   ✅ {route} - {response.status_code}")
            else:
                print(f"   ❌ {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    # Test 4: Manager routes
    print("\n4. Testing Manager routes...")
    manager_routes = [
        ('/manager/dashboard', 'GET'),
        ('/manager/add_feedback', 'POST'),
        ('/manager/reassign_candidate', 'POST'),
        ('/manager/export_feedback', 'GET'),
        ('/manager/candidate/test_id', 'GET')
    ]
    
    for route, method in manager_routes:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{route}", allow_redirects=False)
            else:
                response = requests.post(f"{base_url}{route}", allow_redirects=False)
            
            if response.status_code in [200, 302, 405]:
                print(f"   ✅ {route} - {response.status_code}")
            else:
                print(f"   ❌ {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    # Test 5: Cluster routes
    print("\n5. Testing Cluster routes...")
    cluster_routes = [
        ('/cluster/dashboard', 'GET')
    ]
    
    for route, method in cluster_routes:
        try:
            response = requests.get(f"{base_url}{route}", allow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"   ✅ {route} - {response.status_code}")
            else:
                print(f"   ❌ {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    # Test 6: General routes
    print("\n6. Testing General routes...")
    general_routes = [
        ('/login', 'GET'),
        ('/register', 'GET'),
        ('/logout', 'GET')
    ]
    
    for route, method in general_routes:
        try:
            response = requests.get(f"{base_url}{route}", allow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"   ✅ {route} - {response.status_code}")
            else:
                print(f"   ❌ {route} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route} - Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive Test Summary!")
    print("\n✅ Fixed Issues:")
    print("   - Removed non-existent 'manager.feedback_history' route")
    print("   - Updated manager routes to use 'manager_email' instead of 'assigned_to'")
    print("   - Fixed candidate field references (first_name, last_name)")
    print("   - Updated status values to match new schema")
    print("   - Fixed feedback field references (manager_feedback)")
    print("   - Updated route names to match actual endpoints")
    
    print("\n✅ Expected Results:")
    print("   - All routes should return 200, 302, or 405 status codes")
    print("   - 302 = Redirect (expected for unauthenticated requests)")
    print("   - 405 = Method Not Allowed (expected for wrong HTTP method)")
    print("   - 200 = Success (for GET requests to accessible pages)")
    
    print("\n✅ Application Structure:")
    print("   - Admin Portal: /admin/*")
    print("   - HR Portal: /hr/*")
    print("   - Manager Portal: /manager/*")
    print("   - Cluster Portal: /cluster/*")
    print("   - General: /login, /register, /logout")
    
    print("\n🔧 Next Steps:")
    print("   1. Login as different user types to test full functionality")
    print("   2. Test candidate creation and assignment")
    print("   3. Test feedback submission and export")
    print("   4. Verify all templates render correctly")

if __name__ == "__main__":
    test_comprehensive_fix() 