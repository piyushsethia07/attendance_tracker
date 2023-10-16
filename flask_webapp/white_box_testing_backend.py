
from test import add_class_schedule, add_class, add_teacher, add_module, calculate_break_hours
from test import query_database, update_data_in_database
import pytest
from datetime import datetime

def test_add_class():
    data = {'class': 'Test Class1'}
    result = add_class(data)
    assert result == f"{data['class']} added successfully"

def test_add_teacher():
    data = {'trainer': 'Test Teacher1'}
    result = add_teacher(data)
    assert result == f"{data['trainer']} added successfully"

def test_add_module():
    data = {'module': 'Test Module1'}
    result = add_module(data)
    assert result == f"{data['module']} added successfully"

def test_add_class_schedule():
    data = {
        'class': 'Test Class1',
        'trainer': 'Test Teacher1',
        'module': 'Test Module1',
        'date': "10/14/2023",
        'class total': 20
    }
    result = add_class_schedule(data)
    assert result == "Success"

def test_calculate_break_hours():
    assert calculate_break_hours("Present") == 2.0
    assert calculate_break_hours("Absent") == 0.0
    assert calculate_break_hours("Late_15_mins") == 1.75

def test_query_database():
    # Assuming you have some test data in your database
    result = query_database("TestStudentID", "Test Class", "Test Teacher", "Test Module")
    assert result is None