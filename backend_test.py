#!/usr/bin/env python3
"""
BLS-SPANISH Backend API Testing Suite
Tests the newly implemented visa types selection API and other core functionality
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend .env: {e}")
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_URL = f"{BASE_URL}/api"

class BLSBackendTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def test_root_endpoint(self):
        """Test GET /api/ endpoint"""
        try:
            response = self.session.get(f"{API_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "BLS2" in data.get("message", "") and "version" in data:
                    self.log_test("Root Endpoint", True, f"Version: {data.get('version')}", data)
                else:
                    self.log_test("Root Endpoint", False, "Invalid response format", data)
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")

    def test_visa_types_endpoint(self):
        """Test GET /api/visa-types endpoint - NEW FEATURE"""
        try:
            response = self.session.get(f"{API_URL}/visa-types")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                if "visa_types" not in data or "appointment_types" not in data:
                    self.log_test("Visa Types Endpoint", False, "Missing required fields", data)
                    return
                
                visa_types = data["visa_types"]
                appointment_types = data["appointment_types"]
                
                # Validate visa types structure
                expected_visa_types = ["Tourist Visa", "Business Visa", "Student Visa", "Work Visa", "Family Reunion Visa"]
                expected_appointment_types = ["Individual", "Family"]
                
                missing_visa_types = [vt for vt in expected_visa_types if vt not in visa_types]
                missing_appointment_types = [at for at in expected_appointment_types if at not in appointment_types]
                
                if missing_visa_types or missing_appointment_types:
                    details = f"Missing visa types: {missing_visa_types}, Missing appointment types: {missing_appointment_types}"
                    self.log_test("Visa Types Endpoint", False, details, data)
                else:
                    # Check subtypes for each visa type
                    valid_subtypes = True
                    for visa_type, subtypes in visa_types.items():
                        if not isinstance(subtypes, list) or len(subtypes) == 0:
                            valid_subtypes = False
                            break
                    
                    if valid_subtypes:
                        self.log_test("Visa Types Endpoint", True, f"Found {len(visa_types)} visa types with subtypes", data)
                    else:
                        self.log_test("Visa Types Endpoint", False, "Invalid subtypes structure", data)
            else:
                self.log_test("Visa Types Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Visa Types Endpoint", False, f"Exception: {str(e)}")

    def test_system_config_endpoint(self):
        """Test GET /api/system/config endpoint - NEW FEATURE"""
        try:
            response = self.session.get(f"{API_URL}/system/config")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required configuration fields
                required_fields = ["status", "check_interval_minutes", "visa_type", "visa_subtype", 
                                 "appointment_type", "number_of_members"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("System Config Endpoint", False, f"Missing fields: {missing_fields}", data)
                else:
                    # Validate field values
                    valid_status = data["status"] in ["stopped", "running", "paused", "error"]
                    valid_interval = isinstance(data["check_interval_minutes"], int) and data["check_interval_minutes"] > 0
                    valid_members = isinstance(data["number_of_members"], int) and data["number_of_members"] > 0
                    
                    if valid_status and valid_interval and valid_members:
                        self.log_test("System Config Endpoint", True, 
                                    f"Status: {data['status']}, Interval: {data['check_interval_minutes']}min, "
                                    f"Visa: {data['visa_type']} ({data['visa_subtype']}), "
                                    f"Type: {data['appointment_type']}, Members: {data['number_of_members']}", data)
                    else:
                        self.log_test("System Config Endpoint", False, "Invalid field values", data)
            else:
                self.log_test("System Config Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("System Config Endpoint", False, f"Exception: {str(e)}")

    def test_system_status_endpoint(self):
        """Test GET /api/system/status endpoint"""
        try:
            response = self.session.get(f"{API_URL}/system/status")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["status", "total_checks", "slots_found", "successful_bookings", "error_count"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("System Status Endpoint", False, f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("System Status Endpoint", True, 
                                f"Status: {data['status']}, Checks: {data['total_checks']}, "
                                f"Slots: {data['slots_found']}, Bookings: {data['successful_bookings']}", data)
            else:
                self.log_test("System Status Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("System Status Endpoint", False, f"Exception: {str(e)}")

    def test_system_start_with_visa_config(self):
        """Test POST /api/system/start with new visa configuration parameters - NEW FEATURE"""
        try:
            # Test data as specified in the review request
            test_config = {
                "visa_type": "Business Visa",
                "visa_subtype": "Long Stay", 
                "appointment_type": "Family",
                "number_of_members": 3,
                "check_interval_minutes": 5
            }
            
            response = self.session.post(f"{API_URL}/system/start", json=test_config)
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data and "status" in data:
                    if data["status"] == "running":
                        self.log_test("System Start with Visa Config", True, 
                                    f"System started with config: {test_config}", data)
                        
                        # Wait a moment then verify config was saved
                        time.sleep(2)
                        self.verify_config_saved(test_config)
                    else:
                        self.log_test("System Start with Visa Config", False, 
                                    f"System not running after start: {data['status']}", data)
                else:
                    self.log_test("System Start with Visa Config", False, "Invalid response format", data)
            else:
                self.log_test("System Start with Visa Config", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("System Start with Visa Config", False, f"Exception: {str(e)}")

    def verify_config_saved(self, expected_config: Dict[str, Any]):
        """Verify that the visa configuration was properly saved to database"""
        try:
            response = self.session.get(f"{API_URL}/system/config")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if all expected config values were saved
                config_matches = True
                mismatches = []
                
                for key, expected_value in expected_config.items():
                    if key in data:
                        if data[key] != expected_value:
                            config_matches = False
                            mismatches.append(f"{key}: expected {expected_value}, got {data[key]}")
                    else:
                        config_matches = False
                        mismatches.append(f"{key}: missing from config")
                
                if config_matches:
                    self.log_test("Config Database Persistence", True, 
                                "All visa configuration parameters saved correctly", data)
                else:
                    self.log_test("Config Database Persistence", False, 
                                f"Config mismatches: {mismatches}", data)
            else:
                self.log_test("Config Database Persistence", False, 
                            f"Failed to retrieve config: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Config Database Persistence", False, f"Exception: {str(e)}")

    def test_single_automation_check(self):
        """Test POST /api/test/check-once to verify Playwright browsers are working"""
        try:
            response = self.session.post(f"{API_URL}/test/check-once")
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["success", "slots_found", "method"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Single Automation Check", False, f"Missing fields: {missing_fields}", data)
                else:
                    if data.get("method") == "enhanced_automation":
                        self.log_test("Single Automation Check", True, 
                                    f"Playwright browsers working. Success: {data['success']}, "
                                    f"Slots found: {data['slots_found']}", data)
                    else:
                        self.log_test("Single Automation Check", False, 
                                    f"Unexpected method: {data.get('method')}", data)
            else:
                self.log_test("Single Automation Check", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Single Automation Check", False, f"Exception: {str(e)}")

    def test_system_stop(self):
        """Test POST /api/system/stop endpoint"""
        try:
            response = self.session.post(f"{API_URL}/system/stop")
            
            if response.status_code == 200:
                data = response.json()
                
                if "message" in data and "status" in data:
                    if data["status"] == "stopped":
                        self.log_test("System Stop", True, "System stopped successfully", data)
                    else:
                        self.log_test("System Stop", False, f"System not stopped: {data['status']}", data)
                else:
                    self.log_test("System Stop", False, "Invalid response format", data)
            else:
                self.log_test("System Stop", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("System Stop", False, f"Exception: {str(e)}")

    def test_logs_endpoint(self):
        """Test GET /api/logs endpoint"""
        try:
            response = self.session.get(f"{API_URL}/logs?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                
                if "logs" in data and "total_count" in data:
                    logs = data["logs"]
                    if isinstance(logs, list):
                        self.log_test("Logs Endpoint", True, 
                                    f"Retrieved {len(logs)} logs, Total: {data['total_count']}", 
                                    {"log_count": len(logs), "total_count": data["total_count"]})
                    else:
                        self.log_test("Logs Endpoint", False, "Logs is not a list", data)
                else:
                    self.log_test("Logs Endpoint", False, "Missing required fields", data)
            else:
                self.log_test("Logs Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Logs Endpoint", False, f"Exception: {str(e)}")

    def test_appointments_endpoint(self):
        """Test GET /api/appointments/available endpoint"""
        try:
            response = self.session.get(f"{API_URL}/appointments/available?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                
                if "slots" in data and "total_count" in data:
                    slots = data["slots"]
                    if isinstance(slots, list):
                        self.log_test("Appointments Endpoint", True, 
                                    f"Retrieved {len(slots)} slots, Total: {data['total_count']}", 
                                    {"slot_count": len(slots), "total_count": data["total_count"]})
                    else:
                        self.log_test("Appointments Endpoint", False, "Slots is not a list", data)
                else:
                    self.log_test("Appointments Endpoint", False, "Missing required fields", data)
            else:
                self.log_test("Appointments Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Appointments Endpoint", False, f"Exception: {str(e)}")

    def test_ocr_endpoint(self):
        """Test POST /api/ocr-match endpoint"""
        try:
            # Test with sample data
            test_data = {
                "target": "5",
                "tiles": [
                    {"base64Image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="},
                    {"base64Image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="}
                ],
                "enhanced_mode": False
            }
            
            response = self.session.post(f"{API_URL}/ocr-match", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ["target", "matching_indices", "processed_tiles", "success"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("OCR Endpoint", False, f"Missing fields: {missing_fields}", data)
                else:
                    if data["success"] and isinstance(data["matching_indices"], list):
                        self.log_test("OCR Endpoint", True, 
                                    f"Processed {data['processed_tiles']} tiles, "
                                    f"Found {len(data['matching_indices'])} matches", data)
                    else:
                        self.log_test("OCR Endpoint", False, "OCR processing failed or invalid format", data)
            else:
                self.log_test("OCR Endpoint", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("OCR Endpoint", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting BLS-SPANISH Backend API Tests")
        print(f"Backend URL: {BASE_URL}")
        print(f"API URL: {API_URL}")
        print("=" * 80)
        
        # Test core endpoints
        self.test_root_endpoint()
        
        # Test NEW visa types functionality (priority)
        self.test_visa_types_endpoint()
        self.test_system_config_endpoint()
        self.test_system_start_with_visa_config()
        
        # Test Playwright browser functionality
        self.test_single_automation_check()
        
        # Test existing endpoints
        self.test_system_status_endpoint()
        self.test_logs_endpoint()
        self.test_appointments_endpoint()
        self.test_ocr_endpoint()
        
        # Clean up - stop system
        self.test_system_stop()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("🏁 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = BLSBackendTester()
    tester.run_all_tests()