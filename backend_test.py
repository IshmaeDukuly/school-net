#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for School Management System
Tests all CRUD operations, automatic features, and weighted grade calculations
"""

import requests
import json
from datetime import date, datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE}")

class SchoolManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.created_students = []
        self.created_classes = []
        self.created_assignments = []
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def log_result(self, test_name, success, message=""):
        if success:
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")

    def test_api_connection(self):
        """Test basic API connectivity"""
        print("\n=== Testing API Connection ===")
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "School Management System API" in data.get('message', ''):
                    self.log_result("API Connection", True, "Root endpoint accessible")
                else:
                    self.log_result("API Connection", False, f"Unexpected response: {data}")
            else:
                self.log_result("API Connection", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("API Connection", False, f"Connection error: {str(e)}")

    def test_dashboard_stats(self):
        """Test dashboard statistics API"""
        print("\n=== Testing Dashboard Statistics ===")
        try:
            response = self.session.get(f"{API_BASE}/dashboard")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_students', 'total_classes', 'total_assignments', 
                                 'average_class_performance', 'recent_grades_count']
                
                missing_fields = [field for field in required_fields if field not in data]
                if not missing_fields:
                    self.log_result("Dashboard Stats", True, f"All fields present: {data}")
                else:
                    self.log_result("Dashboard Stats", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Dashboard Stats", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Dashboard Stats", False, f"Error: {str(e)}")

    def test_student_management(self):
        """Test student CRUD operations"""
        print("\n=== Testing Student Management ===")
        
        # Test creating students
        test_students = [
            {
                "student_id": "STU001",
                "first_name": "Emma",
                "last_name": "Johnson",
                "email": "emma.johnson@email.com",
                "grade_level": "K",
                "parent_name": "Sarah Johnson",
                "parent_email": "sarah.johnson@email.com",
                "parent_phone": "555-0101"
            },
            {
                "student_id": "STU002", 
                "first_name": "Liam",
                "last_name": "Smith",
                "email": "liam.smith@email.com",
                "grade_level": "1",
                "parent_name": "Michael Smith",
                "parent_email": "michael.smith@email.com",
                "parent_phone": "555-0102"
            },
            {
                "student_id": "STU003",
                "first_name": "Olivia",
                "last_name": "Brown",
                "email": "olivia.brown@email.com", 
                "grade_level": "2",
                "parent_name": "Jennifer Brown",
                "parent_email": "jennifer.brown@email.com",
                "parent_phone": "555-0103"
            }
        ]

        for student_data in test_students:
            try:
                response = self.session.post(f"{API_BASE}/students", json=student_data)
                if response.status_code == 200:
                    student = response.json()
                    self.created_students.append(student)
                    self.log_result(f"Create Student {student_data['student_id']}", True, 
                                  f"Created with ID: {student['id']}")
                else:
                    self.log_result(f"Create Student {student_data['student_id']}", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result(f"Create Student {student_data['student_id']}", False, f"Error: {str(e)}")

        # Test duplicate student ID handling
        if test_students:
            try:
                response = self.session.post(f"{API_BASE}/students", json=test_students[0])
                if response.status_code == 400:
                    self.log_result("Duplicate Student ID Handling", True, "Correctly rejected duplicate")
                else:
                    self.log_result("Duplicate Student ID Handling", False, 
                                  f"Should have returned 400, got {response.status_code}")
            except Exception as e:
                self.log_result("Duplicate Student ID Handling", False, f"Error: {str(e)}")

        # Test fetching students
        try:
            response = self.session.get(f"{API_BASE}/students")
            if response.status_code == 200:
                students = response.json()
                if len(students) >= len(test_students):
                    self.log_result("Fetch Students", True, f"Retrieved {len(students)} students")
                else:
                    self.log_result("Fetch Students", False, f"Expected at least {len(test_students)}, got {len(students)}")
            else:
                self.log_result("Fetch Students", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Fetch Students", False, f"Error: {str(e)}")

    def test_class_management(self):
        """Test class creation with automatic grade categories"""
        print("\n=== Testing Class Management ===")
        
        test_classes = [
            {
                "name": "Kindergarten Math",
                "subject": "Mathematics", 
                "teacher_name": "Mrs. Anderson",
                "grade_level": "K",
                "school_year": "2024-2025"
            },
            {
                "name": "First Grade Reading",
                "subject": "English Language Arts",
                "teacher_name": "Mr. Wilson", 
                "grade_level": "1",
                "school_year": "2024-2025"
            },
            {
                "name": "Second Grade Science",
                "subject": "Science",
                "teacher_name": "Ms. Davis",
                "grade_level": "2", 
                "school_year": "2024-2025"
            }
        ]

        for class_data in test_classes:
            try:
                response = self.session.post(f"{API_BASE}/classes", json=class_data)
                if response.status_code == 200:
                    class_obj = response.json()
                    self.created_classes.append(class_obj)
                    self.log_result(f"Create Class {class_data['name']}", True, 
                                  f"Created with ID: {class_obj['id']}")
                    
                    # Test automatic grade category creation
                    try:
                        cat_response = self.session.get(f"{API_BASE}/classes/{class_obj['id']}/categories")
                        if cat_response.status_code == 200:
                            categories = cat_response.json()
                            expected_categories = ["Homework", "Tests", "Projects"]
                            category_names = [cat['name'] for cat in categories]
                            
                            if all(cat in category_names for cat in expected_categories):
                                # Check weights
                                weights = {cat['name']: cat['weight_percentage'] for cat in categories}
                                expected_weights = {"Homework": 30.0, "Tests": 50.0, "Projects": 20.0}
                                
                                if weights == expected_weights:
                                    self.log_result(f"Auto Grade Categories {class_data['name']}", True, 
                                                  f"Correct categories and weights: {weights}")
                                else:
                                    self.log_result(f"Auto Grade Categories {class_data['name']}", False, 
                                                  f"Wrong weights. Expected: {expected_weights}, Got: {weights}")
                            else:
                                self.log_result(f"Auto Grade Categories {class_data['name']}", False, 
                                              f"Missing categories. Expected: {expected_categories}, Got: {category_names}")
                        else:
                            self.log_result(f"Auto Grade Categories {class_data['name']}", False, 
                                          f"Failed to fetch categories: {cat_response.status_code}")
                    except Exception as e:
                        self.log_result(f"Auto Grade Categories {class_data['name']}", False, f"Error: {str(e)}")
                        
                else:
                    self.log_result(f"Create Class {class_data['name']}", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result(f"Create Class {class_data['name']}", False, f"Error: {str(e)}")

        # Test fetching classes
        try:
            response = self.session.get(f"{API_BASE}/classes")
            if response.status_code == 200:
                classes = response.json()
                if len(classes) >= len(test_classes):
                    self.log_result("Fetch Classes", True, f"Retrieved {len(classes)} classes")
                else:
                    self.log_result("Fetch Classes", False, f"Expected at least {len(test_classes)}, got {len(classes)}")
            else:
                self.log_result("Fetch Classes", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Fetch Classes", False, f"Error: {str(e)}")

    def test_assignment_creation(self):
        """Test assignment creation with automatic grade record creation"""
        print("\n=== Testing Assignment Creation ===")
        
        if not self.created_classes:
            self.log_result("Assignment Creation", False, "No classes available for testing")
            return

        test_assignments = [
            {
                "name": "Math Worksheet 1",
                "description": "Basic addition and subtraction problems",
                "category": "Homework",
                "points_possible": 20.0,
                "due_date": "2024-12-20"
            },
            {
                "name": "Reading Comprehension Test",
                "description": "Test on story understanding",
                "category": "Tests", 
                "points_possible": 100.0,
                "due_date": "2024-12-22"
            },
            {
                "name": "Science Fair Project",
                "description": "Create a volcano model",
                "category": "Projects",
                "points_possible": 50.0,
                "due_date": "2024-12-25"
            }
        ]

        for i, assignment_data in enumerate(test_assignments):
            if i < len(self.created_classes):
                class_obj = self.created_classes[i]
                assignment_data["class_id"] = class_obj["id"]
                
                try:
                    response = self.session.post(f"{API_BASE}/assignments", json=assignment_data)
                    if response.status_code == 200:
                        assignment = response.json()
                        self.created_assignments.append(assignment)
                        self.log_result(f"Create Assignment {assignment_data['name']}", True, 
                                      f"Created with ID: {assignment['id']}")
                        
                        # Test automatic grade record creation
                        # Get students in the same grade level as this class
                        grade_level = class_obj["grade_level"]
                        students_in_grade = [s for s in self.created_students if s["grade_level"] == grade_level]
                        
                        if students_in_grade:
                            # Check if grade records were created for these students
                            student_id = students_in_grade[0]["id"]
                            try:
                                grades_response = self.session.get(f"{API_BASE}/students/{student_id}/grades")
                                if grades_response.status_code == 200:
                                    grades = grades_response.json()
                                    assignment_grades = [g for g in grades if g["assignment_id"] == assignment["id"]]
                                    
                                    if assignment_grades:
                                        self.log_result(f"Auto Grade Records {assignment_data['name']}", True, 
                                                      f"Grade records created for students")
                                    else:
                                        self.log_result(f"Auto Grade Records {assignment_data['name']}", False, 
                                                      f"No grade records found for assignment")
                                else:
                                    self.log_result(f"Auto Grade Records {assignment_data['name']}", False, 
                                                  f"Failed to fetch student grades: {grades_response.status_code}")
                            except Exception as e:
                                self.log_result(f"Auto Grade Records {assignment_data['name']}", False, f"Error: {str(e)}")
                        
                    else:
                        self.log_result(f"Create Assignment {assignment_data['name']}", False, 
                                      f"Status: {response.status_code}, Response: {response.text}")
                except Exception as e:
                    self.log_result(f"Create Assignment {assignment_data['name']}", False, f"Error: {str(e)}")

    def test_grade_entry(self):
        """Test grade entry and percentage calculations"""
        print("\n=== Testing Grade Entry and Calculations ===")
        
        if not self.created_assignments or not self.created_students:
            self.log_result("Grade Entry", False, "No assignments or students available for testing")
            return

        # Test grade entry with percentage calculation
        test_grades = [
            {"points_earned": 18.0, "expected_percentage": 90.0},  # 18/20 = 90%
            {"points_earned": 85.0, "expected_percentage": 85.0},  # 85/100 = 85%
            {"points_earned": 45.0, "expected_percentage": 90.0},  # 45/50 = 90%
        ]

        for i, grade_data in enumerate(test_grades):
            if i < len(self.created_assignments) and i < len(self.created_students):
                assignment = self.created_assignments[i]
                student = self.created_students[i]
                
                grade_payload = {
                    "student_id": student["id"],
                    "assignment_id": assignment["id"],
                    "points_earned": grade_data["points_earned"],
                    "is_submitted": True,
                    "submission_date": "2024-12-15"
                }
                
                try:
                    response = self.session.post(f"{API_BASE}/grades", json=grade_payload)
                    if response.status_code == 200:
                        grade = response.json()
                        calculated_percentage = grade.get("percentage")
                        
                        if calculated_percentage == grade_data["expected_percentage"]:
                            self.log_result(f"Grade Calculation {assignment['name']}", True, 
                                          f"Correct percentage: {calculated_percentage}%")
                        else:
                            self.log_result(f"Grade Calculation {assignment['name']}", False, 
                                          f"Expected {grade_data['expected_percentage']}%, got {calculated_percentage}%")
                    else:
                        self.log_result(f"Grade Entry {assignment['name']}", False, 
                                      f"Status: {response.status_code}, Response: {response.text}")
                except Exception as e:
                    self.log_result(f"Grade Entry {assignment['name']}", False, f"Error: {str(e)}")

        # Test edge case: zero points possible
        if self.created_classes and self.created_students:
            zero_points_assignment = {
                "class_id": self.created_classes[0]["id"],
                "name": "Participation Credit",
                "description": "Just for showing up",
                "category": "Participation",
                "points_possible": 0.0
            }
            
            try:
                response = self.session.post(f"{API_BASE}/assignments", json=zero_points_assignment)
                if response.status_code == 200:
                    assignment = response.json()
                    
                    # Try to enter a grade for zero points assignment
                    grade_payload = {
                        "student_id": self.created_students[0]["id"],
                        "assignment_id": assignment["id"],
                        "points_earned": 0.0,
                        "is_submitted": True
                    }
                    
                    grade_response = self.session.post(f"{API_BASE}/grades", json=grade_payload)
                    if grade_response.status_code == 200:
                        grade = grade_response.json()
                        if grade.get("percentage") == 0.0:
                            self.log_result("Zero Points Assignment", True, "Handled zero points correctly")
                        else:
                            self.log_result("Zero Points Assignment", False, 
                                          f"Expected 0%, got {grade.get('percentage')}%")
                    else:
                        self.log_result("Zero Points Assignment", False, f"Grade entry failed: {grade_response.status_code}")
            except Exception as e:
                self.log_result("Zero Points Assignment", False, f"Error: {str(e)}")

    def test_progress_reports(self):
        """Test progress report generation with weighted calculations"""
        print("\n=== Testing Progress Reports ===")
        
        if not self.created_students or not self.created_classes:
            self.log_result("Progress Reports", False, "No students or classes available for testing")
            return

        # Test progress report for first student in first class
        student = self.created_students[0]
        class_obj = self.created_classes[0]
        
        try:
            response = self.session.get(f"{API_BASE}/students/{student['id']}/progress/{class_obj['id']}")
            if response.status_code == 200:
                report = response.json()
                
                # Check required fields
                required_fields = ['student_id', 'student_name', 'class_id', 'class_name', 
                                 'overall_percentage', 'letter_grade', 'category_grades',
                                 'total_assignments', 'completed_assignments', 'missing_assignments']
                
                missing_fields = [field for field in required_fields if field not in report]
                if not missing_fields:
                    self.log_result("Progress Report Structure", True, "All required fields present")
                    
                    # Check letter grade calculation
                    percentage = report['overall_percentage']
                    letter_grade = report['letter_grade']
                    expected_letter = self.get_expected_letter_grade(percentage)
                    
                    if letter_grade == expected_letter:
                        self.log_result("Letter Grade Calculation", True, 
                                      f"{percentage}% = {letter_grade}")
                    else:
                        self.log_result("Letter Grade Calculation", False, 
                                      f"{percentage}% should be {expected_letter}, got {letter_grade}")
                    
                    # Check category grades structure
                    category_grades = report['category_grades']
                    if isinstance(category_grades, dict):
                        self.log_result("Category Grades Structure", True, 
                                      f"Categories: {list(category_grades.keys())}")
                    else:
                        self.log_result("Category Grades Structure", False, 
                                      f"Expected dict, got {type(category_grades)}")
                    
                    # Log the full report for verification
                    print(f"📊 Progress Report Sample:")
                    print(f"   Student: {report['student_name']}")
                    print(f"   Class: {report['class_name']}")
                    print(f"   Overall: {report['overall_percentage']}% ({report['letter_grade']})")
                    print(f"   Categories: {report['category_grades']}")
                    print(f"   Assignments: {report['completed_assignments']}/{report['total_assignments']} completed")
                    
                else:
                    self.log_result("Progress Report Structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Progress Reports", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Progress Reports", False, f"Error: {str(e)}")

    def get_expected_letter_grade(self, percentage):
        """Helper to calculate expected letter grade"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"

    def test_error_handling(self):
        """Test error handling for invalid data"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid student ID
        try:
            response = self.session.get(f"{API_BASE}/students/invalid-id")
            if response.status_code == 404:
                self.log_result("Invalid Student ID", True, "Correctly returned 404")
            else:
                self.log_result("Invalid Student ID", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Student ID", False, f"Error: {str(e)}")

        # Test invalid assignment data
        invalid_assignment = {
            "class_id": "invalid-class-id",
            "name": "Test Assignment",
            "category": "InvalidCategory",
            "points_possible": -10.0  # Negative points
        }
        
        try:
            response = self.session.post(f"{API_BASE}/assignments", json=invalid_assignment)
            if response.status_code >= 400:
                self.log_result("Invalid Assignment Data", True, f"Correctly rejected with {response.status_code}")
            else:
                self.log_result("Invalid Assignment Data", False, f"Should have rejected, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid Assignment Data", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Backend API Tests")
        print("=" * 60)
        
        self.test_api_connection()
        self.test_dashboard_stats()
        self.test_student_management()
        self.test_class_management()
        self.test_assignment_creation()
        self.test_grade_entry()
        self.test_progress_reports()
        self.test_error_handling()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📊 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print(f"\n🔍 Failed Tests:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = SchoolManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All tests passed! Backend is working correctly.")
        exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Check the details above.")
        exit(1)