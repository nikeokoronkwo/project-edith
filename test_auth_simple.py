#!/usr/bin/env python3
"""
Simple authenticated frontend testing using requests
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:3000"
LOGIN_EMAIL = "nick.fury@shield.gov"
LOGIN_PASSWORD = "shield123"

def test_login():
    """Test login functionality"""
    print(f"\n{'='*60}")
    print("Step 1: Testing Login")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/auth/sign-in/email"
    payload = {
        "email": LOGIN_EMAIL,
        "password": LOGIN_PASSWORD
    }
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login Successful!")
            print(f"User: {data.get('user', {}).get('name')}")
            print(f"Email: {data.get('user', {}).get('email')}")
            print(f"User ID: {data.get('user', {}).get('id')}")
            
            # Check cookies
            if 'set-cookie' in response.headers:
                print(f"\n🍪 Cookies Set:")
                for cookie in response.headers.get('set-cookie', '').split(','):
                    if 'better-auth' in cookie:
                        print(f"  - {cookie[:80]}...")
            
            return response.cookies
        else:
            print(f"❌ Login Failed")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_page(url, cookies, page_name):
    """Test a specific page"""
    print(f"\n{'='*60}")
    print(f"Testing: {page_name}")
    print(f"{'='*60}")
    print(f"GET {url}")
    
    try:
        response = requests.get(url, cookies=cookies, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Page loaded successfully")
            print(f"Content length: {len(content)} bytes")
            
            # Check for redirects in HTML
            if '<meta http-equiv="refresh"' in content:
                print("⚠️  HTML meta refresh detected (redirecting to login)")
                return False
            
            # Check if it's the actual page or login redirect
            if 'Agent Authentication' in content or 'agent@shield.gov' in content:
                print("⚠️  Redirected to login page (authentication failed)")
                return False
            
            # Check for data indicators
            print("\n📊 Content Analysis:")
            
            # Resources
            resources = ["vibranium", "arc_fuel", "medical", "energy_cells", "serum"]
            found = [r for r in resources if r in content.lower()]
            if found:
                print(f"  - Resources found: {', '.join(found)}")
            
            # Check for page title
            if '<title>' in content:
                title_start = content.find('<title>') + 7
                title_end = content.find('</title>', title_start)
                title = content[title_start:title_end]
                print(f"  - Page title: {title}")
            
            # Check for form elements
            if '<form' in content:
                form_count = content.count('<form')
                print(f"  - Forms found: {form_count}")
            
            # Check for tables
            if '<table' in content:
                table_count = content.count('<table')
                print(f"  - Tables found: {table_count}")
            
            # Check for data
            if 'window.__NUXT__' in content:
                print(f"  - ✅ Nuxt data payload present")
            
            return True
            
        elif response.status_code == 302 or response.status_code == 301:
            location = response.headers.get('location', 'unknown')
            print(f"⚠️  Redirect to: {location}")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_report_submission(cookies):
    """Test report submission"""
    print(f"\n{'='*60}")
    print("Step 4: Testing Report Submission")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/reports/new"
    payload = {
        "hero_alias": "Nick Fury",
        "description": "Critical vibranium shortage in Wakanda sector",
        "resource": "vibranium",
        "sector": "WEST_AFRICA"
    }
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, cookies=cookies)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✅ Report submitted successfully!")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response: {response.text[:200]}")
            return True
        else:
            print(f"❌ Submission failed")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print(f"\n{'#'*60}")
    print(f"# Authenticated Frontend Testing (Requests Method)")
    print(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# Base URL: {BASE_URL}")
    print(f"{'#'*60}")
    
    # Step 1: Login
    cookies = test_login()
    
    if not cookies:
        print("\n❌ Cannot proceed without successful login")
        return
    
    # Step 2-3: Test authenticated pages
    pages = [
        ("/dashboard", "Dashboard"),
        ("/reports", "Reports List"),
        ("/reports/new", "New Report Form"),
        ("/analytics", "Analytics"),
    ]
    
    results = {}
    for path, name in pages:
        url = f"{BASE_URL}{path}"
        success = test_page(url, cookies, name)
        results[name] = success
    
    # Step 4: Test report submission
    report_success = test_report_submission(cookies)
    results["Report Submission"] = report_success
    
    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}\n")
    
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    # Note about limitations
    print(f"\n{'='*60}")
    print("NOTE: This is a basic HTTP test without JavaScript execution.")
    print("For full testing (charts, interactivity, etc.), use a browser.")
    print("Playwright installation may still be in progress.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
