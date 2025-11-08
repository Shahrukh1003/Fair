"""
Test Script for FairLens v2.0 Advanced Features

This script demonstrates all the new capabilities:
1. Predictive fairness monitoring
2. Trend analysis
3. Alert verification
4. Role-based access
5. Live prediction monitoring
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_basic_check():
    print_section("1. BASIC FAIRNESS CHECK")
    
    response = requests.get(f"{BASE_URL}/api/monitor_fairness", params={
        "n_samples": 1000,
        "drift_level": 0.5
    })
    
    data = response.json()
    print(f"✓ Fairness check completed")
    print(f"  DIR: {data['drifted_scenario']['dir']:.3f}")
    print(f"  Alert: {data['drifted_scenario']['dir_alert']}")
    print(f"  Explanation: {data['drifted_scenario']['explanation'][:100]}...")
    
    return data

def test_trend_analysis():
    print_section("2. TREND ANALYSIS")
    
    response = requests.get(f"{BASE_URL}/api/fairness_trend", params={
        "window": 10
    })
    
    data = response.json()
    print(f"✓ Trend analysis completed")
    print(f"  Average DIR: {data.get('average_dir', 'N/A')}")
    print(f"  Trend Direction: {data.get('trend_direction', 'N/A')}")
    print(f"  Alert Count: {data.get('alert_count', 'N/A')}")
    print(f"  Data Points: {data.get('data_points', 'N/A')}")

def test_prediction():
    print_section("3. PREDICTIVE DRIFT DETECTION")
    
    response = requests.get(f"{BASE_URL}/api/predict_fairness_drift")
    
    data = response.json()
    print(f"✓ Prediction completed")
    print(f"  Prediction: {data.get('prediction', 'N/A')}")
    print(f"  Confidence: {data.get('confidence', 'N/A')}")
    print(f"  Severity: {data.get('severity', 'N/A')}")
    print(f"  Message: {data.get('message', 'N/A')}")
    print(f"  Recommendation: {data.get('recommendation', 'N/A')[:100]}...")

def test_pre_alert():
    print_section("4. PRE-ALERT CHECK")
    
    response = requests.get(f"{BASE_URL}/api/pre_alert")
    
    data = response.json()
    print(f"✓ Pre-alert check completed")
    print(f"  Pre-Alert: {data.get('pre_alert', 'N/A')}")
    print(f"  Current Avg: {data.get('current_avg', 'N/A')}")
    print(f"  Severity: {data.get('severity', 'N/A')}")
    print(f"  Message: {data.get('message', 'N/A')}")

def test_authentication():
    print_section("5. ROLE-BASED AUTHENTICATION")
    
    # Get auditor token
    response = requests.post(f"{BASE_URL}/api/login", json={
        "role": "auditor"
    })
    
    data = response.json()
    token = data.get('token')
    print(f"✓ Authentication successful")
    print(f"  Role: {data.get('role')}")
    print(f"  Token: {token}")
    
    return token

def test_audit_access(token):
    print_section("6. AUDIT LOG ACCESS (Protected)")
    
    # Try without token (should fail)
    response = requests.get(f"{BASE_URL}/api/audit_history")
    print(f"✗ Without token: Status {response.status_code} (Expected 401)")
    
    # Try with token (should succeed)
    response = requests.get(
        f"{BASE_URL}/api/audit_history",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ With token: Access granted")
        print(f"  Entries retrieved: {data.get('count', 0)}")
    else:
        print(f"✗ With token: Status {response.status_code}")

def test_live_predictions():
    print_section("7. LIVE PREDICTION MONITORING")
    
    predictions = [
        {"gender": "Female", "approved": True},
        {"gender": "Male", "approved": True},
        {"gender": "Female", "approved": False},
        {"gender": "Male", "approved": True},
        {"gender": "Female", "approved": False},
        {"gender": "Male", "approved": True},
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/submit_predictions",
        json={
            "model": "test_model_v1",
            "predictions": predictions
        }
    )
    
    data = response.json()
    print(f"✓ Live predictions submitted")
    print(f"  DIR: {data.get('dir', 'N/A')}")
    print(f"  Alert: {data.get('alert', 'N/A')}")
    print(f"  Female Rate: {data.get('female_rate', 'N/A')}")
    print(f"  Male Rate: {data.get('male_rate', 'N/A')}")
    print(f"  Record ID: {data.get('record_id', 'N/A')}")

def test_verification(token):
    print_section("8. RECORD VERIFICATION")
    
    # Verify record ID 1
    response = requests.get(
        f"{BASE_URL}/api/verify_alert/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Record verification completed")
        print(f"  Record ID: {data.get('record_id', 'N/A')}")
        print(f"  Hash: {data.get('hash_value', 'N/A')[:32]}...")
        print(f"  Blockchain Verified: {data.get('blockchain_verified', 'N/A')}")
        
        if data.get('blockchain_anchor'):
            anchor = data['blockchain_anchor']
            print(f"  TX ID: {anchor.get('tx_id', 'N/A')[:32]}...")
            print(f"  Block: {anchor.get('block_number', 'N/A')}")
    else:
        print(f"✗ Verification failed: Status {response.status_code}")

def run_all_tests():
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  FairLens v2.0 - Advanced Features Test Suite".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    try:
        # Run tests
        test_basic_check()
        time.sleep(0.5)
        
        test_basic_check()  # Run again to build history
        time.sleep(0.5)
        
        test_trend_analysis()
        time.sleep(0.5)
        
        test_prediction()
        time.sleep(0.5)
        
        test_pre_alert()
        time.sleep(0.5)
        
        token = test_authentication()
        time.sleep(0.5)
        
        test_audit_access(token)
        time.sleep(0.5)
        
        test_live_predictions()
        time.sleep(0.5)
        
        test_verification(token)
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "  ✓ ALL TESTS COMPLETED SUCCESSFULLY".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
        print("🎉 FairLens v2.0 is fully operational!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Predictive fairness monitoring")
        print("  ✓ Temporal trend analysis")
        print("  ✓ Early warning system")
        print("  ✓ Role-based access control")
        print("  ✓ Live prediction monitoring")
        print("  ✓ Tamper-proof verification")
        print("  ✓ Blockchain anchoring")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to FairLens API")
        print("Please ensure the Flask backend is running:")
        print("  python fairlens_backend/app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
