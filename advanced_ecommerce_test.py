#!/usr/bin/env python3
"""
Advanced E-commerce Features (Phase 7) - Permission Fix Testing
Testing admin endpoints that were previously failing with 403 Forbidden
Now testing with updated super admin permissions (23 permissions)
"""

import requests
import sys
from datetime import datetime
import json
import uuid

class AdvancedEcommerceAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=10)

            print(f"Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response Data: {json.dumps(response_data, indent=2)[:300]}...")
                    return success, response_data
                except:
                    print(f"Response Text: {response.text[:200]}...")
                    return success, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"Response Text: {response.text[:500]}...")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login to get authentication token"""
        login_data = {
            "email": "admin@niteputterpro.com",
            "password": "superadmin123"
        }
        
        success, response_data = self.run_test(
            "Admin Login (Get Token)",
            "POST",
            "api/admin/auth/login",
            200,
            data=login_data
        )
        
        if success and response_data:
            self.admin_token = response_data.get('access_token')
            permissions = response_data.get('permissions', [])
            admin_data = response_data.get('admin', {})
            
            print(f"✅ Admin authenticated successfully")
            print(f"✅ Admin role: {admin_data.get('role')}")
            print(f"✅ Admin permissions count: {len(permissions)}")
            print(f"✅ Permissions include e-commerce: {any('manage_' in p or 'view_' in p for p in permissions)}")
            
            return True, response_data
        
        return False, {}

    # ========== ADVANCED E-COMMERCE FEATURES TESTS ==========
    
    def test_admin_coupon_create(self):
        """Test POST /api/admin/coupons - Create coupons (admin only) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        coupon_data = {
            "code": "TESTCOUPON10",
            "name": "Test Coupon 10% Off",
            "description": "Test coupon for 10% discount",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "minimum_order_amount": 50.0,
            "maximum_discount_amount": 25.0,
            "usage_limit": 100,
            "usage_limit_per_customer": 1,
            "valid_from": "2024-01-01T00:00:00Z",
            "valid_until": "2024-12-31T23:59:59Z",
            "is_active": True,
            "applicable_products": [],
            "applicable_categories": []
        }
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin Create Coupon (Previously 403)",
            "POST",
            "api/admin/coupons",
            200,
            data=coupon_data,
            headers=headers
        )
    
    def test_admin_coupon_list(self):
        """Test GET /api/admin/coupons - List coupons (admin only) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin List Coupons (Previously 403)",
            "GET",
            "api/admin/coupons",
            200,
            headers=headers
        )
    
    def test_admin_shipping_zone_create(self):
        """Test POST /api/admin/shipping/zones - Create shipping zones (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        zone_data = {
            "name": "Test Zone USA",
            "description": "Test shipping zone for USA",
            "countries": ["US"],
            "states": ["TX", "CA", "NY"],
            "postal_codes": ["75032", "90210", "10001"],
            "is_active": True
        }
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin Create Shipping Zone (Previously 403)",
            "POST",
            "api/admin/shipping/zones",
            200,
            data=zone_data,
            headers=headers
        )
    
    def test_admin_shipping_rate_create(self):
        """Test POST /api/admin/shipping/rates - Create shipping rates (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        rate_data = {
            "zone_id": "test-zone-id",
            "name": "Standard Shipping",
            "description": "Standard shipping rate",
            "rate_type": "flat_rate",
            "cost": 9.99,
            "free_shipping_threshold": 100.0,
            "estimated_delivery_days": 5,
            "weight_based_pricing": [],
            "is_active": True
        }
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin Create Shipping Rate (Previously 403)",
            "POST",
            "api/admin/shipping/rates",
            200,
            data=rate_data,
            headers=headers
        )
    
    def test_admin_tax_rule_create(self):
        """Test POST /api/admin/tax/rules - Create tax rules (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        tax_data = {
            "name": "Texas Sales Tax",
            "description": "Sales tax for Texas",
            "tax_rate": 8.25,
            "countries": ["US"],
            "states": ["TX"],
            "cities": ["Dallas", "Houston"],
            "postal_codes": ["75032"],
            "product_categories": [],
            "is_active": True
        }
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin Create Tax Rule (Previously 403)",
            "POST",
            "api/admin/tax/rules",
            200,
            data=tax_data,
            headers=headers
        )
    
    def test_admin_returns_list(self):
        """Test GET /api/admin/returns - Get all returns (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin Get All Returns (Previously 403)",
            "GET",
            "api/admin/returns",
            200,
            headers=headers
        )
    
    def test_admin_ecommerce_stats(self):
        """Test GET /api/admin/ecommerce/stats - E-commerce statistics (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin E-commerce Stats (Previously 403)",
            "GET",
            "api/admin/ecommerce/stats",
            200,
            headers=headers
        )
    
    def test_admin_ecommerce_dashboard(self):
        """Test GET /api/admin/ecommerce/dashboard - E-commerce dashboard (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin E-commerce Dashboard (Previously 403)",
            "GET",
            "api/admin/ecommerce/dashboard",
            200,
            headers=headers
        )
    
    def test_admin_inventory_alerts(self):
        """Test GET /api/admin/inventory/alerts - Low stock alerts (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin Inventory Alerts (Previously 403)",
            "GET",
            "api/admin/inventory/alerts",
            200,
            headers=headers
        )
    
    def test_admin_stock_movement(self):
        """Test POST /api/admin/inventory/stock-movement - Stock movement logging (admin) - Previously failing with 403"""
        if not self.admin_token:
            print("❌ No admin token available, skipping test")
            return False, {}
        
        movement_data = {
            "product_id": "test-product-id",
            "movement_type": "adjustment",
            "quantity_change": 10,
            "new_stock_level": 100,
            "reason": "Inventory adjustment for testing",
            "reference_id": "TEST-REF-001"
        }
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        return self.run_test(
            "Admin Stock Movement (Previously 403)",
            "POST",
            "api/admin/inventory/stock-movement",
            200,
            data=movement_data,
            headers=headers
        )

    def run_focused_tests(self):
        """Run focused tests on Advanced E-commerce Features (Phase 7) that were previously failing"""
        print("🛍️ ADVANCED E-COMMERCE FEATURES (PHASE 7) - PERMISSION FIX TESTING")
        print("=" * 80)
        print("Testing admin endpoints that were previously failing with 403 Forbidden")
        print("Now testing with updated super admin permissions (23 permissions)")
        print("-" * 80)
        
        # First ensure we have admin authentication
        print("🔐 Getting admin authentication...")
        admin_success, admin_response = self.test_admin_login()
        if not admin_success:
            print("❌ Failed to authenticate as admin - cannot proceed with tests")
            return
        
        # Test the previously failing admin endpoints
        test_results = []
        
        print("\n📋 COUPON MANAGEMENT TESTS")
        print("-" * 40)
        success1, _ = self.test_admin_coupon_create()
        test_results.append(("Admin Coupon Create", success1))
        
        success2, _ = self.test_admin_coupon_list()
        test_results.append(("Admin Coupon List", success2))
        
        print("\n🚚 SHIPPING MANAGEMENT TESTS")
        print("-" * 40)
        success3, _ = self.test_admin_shipping_zone_create()
        test_results.append(("Admin Shipping Zone Create", success3))
        
        success4, _ = self.test_admin_shipping_rate_create()
        test_results.append(("Admin Shipping Rate Create", success4))
        
        print("\n💰 TAX MANAGEMENT TESTS")
        print("-" * 40)
        success5, _ = self.test_admin_tax_rule_create()
        test_results.append(("Admin Tax Rule Create", success5))
        
        print("\n🔄 RETURNS MANAGEMENT TESTS")
        print("-" * 40)
        success6, _ = self.test_admin_returns_list()
        test_results.append(("Admin Returns List", success6))
        
        print("\n📊 E-COMMERCE ANALYTICS TESTS")
        print("-" * 40)
        success7, _ = self.test_admin_ecommerce_stats()
        test_results.append(("Admin E-commerce Stats", success7))
        
        success8, _ = self.test_admin_ecommerce_dashboard()
        test_results.append(("Admin E-commerce Dashboard", success8))
        
        print("\n📦 INVENTORY MANAGEMENT TESTS")
        print("-" * 40)
        success9, _ = self.test_admin_inventory_alerts()
        test_results.append(("Admin Inventory Alerts", success9))
        
        success10, _ = self.test_admin_stock_movement()
        test_results.append(("Admin Stock Movement", success10))
        
        # Summary of results
        print("\n" + "=" * 80)
        print("🏁 ADVANCED E-COMMERCE FEATURES TESTING COMPLETE!")
        print("-" * 80)
        
        passed_tests = sum(1 for _, success in test_results if success)
        total_tests = len(test_results)
        
        print(f"📊 Results: {passed_tests}/{total_tests} tests passed")
        
        print("\n📋 DETAILED RESULTS:")
        for test_name, success in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {status} - {test_name}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL ADVANCED E-COMMERCE TESTS PASSED! 🎉")
            print("✅ Permission issues have been resolved!")
        else:
            failed_tests = total_tests - passed_tests
            print(f"\n⚠️  {failed_tests} tests still failing")
            print("❌ Some permission or data model issues may remain")
            
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"✅ Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = AdvancedEcommerceAPITester()
    passed, total = tester.run_focused_tests()
    
    # Exit with appropriate code
    if passed == total:
        print("\n🎉 All tests passed! Permission issues resolved.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} tests failed. Issues remain.")
        sys.exit(1)