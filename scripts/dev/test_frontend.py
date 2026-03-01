#!/usr/bin/env python3
"""
Frontend Testing Script for Nuxt Application
Visits all pages and captures screenshots + error information
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

# Pages to test
PAGES = [
    {"path": "/", "name": "homepage"},
    {"path": "/login", "name": "login"},
    {"path": "/dashboard", "name": "dashboard"},
    {"path": "/reports", "name": "reports"},
    {"path": "/reports/new", "name": "new_report"},
    {"path": "/analytics", "name": "analytics"},
]

BASE_URL = "http://localhost:3000"
OUTPUT_DIR = "frontend_test_results"


async def test_page(page, page_info):
    """Test a single page and capture screenshot + errors"""
    url = f"{BASE_URL}{page_info['path']}"
    name = page_info['name']
    
    print(f"\n{'='*60}")
    print(f"Testing: {name} ({url})")
    print(f"{'='*60}")
    
    results = {
        "name": name,
        "url": url,
        "errors": [],
        "console_logs": [],
        "redirected": False,
        "final_url": None,
        "status_code": None,
        "screenshot": None,
    }
    
    # Listen for console messages
    page.on("console", lambda msg: results["console_logs"].append({
        "type": msg.type,
        "text": msg.text
    }))
    
    # Listen for page errors
    page.on("pageerror", lambda err: results["errors"].append({
        "type": "page_error",
        "message": str(err)
    }))
    
    try:
        # Navigate to the page
        response = await page.goto(url, wait_until="networkidle", timeout=10000)
        results["status_code"] = response.status if response else None
        
        # Wait a bit for any dynamic content
        await page.wait_for_timeout(2000)
        
        # Check if we were redirected
        results["final_url"] = page.url
        if page.url != url:
            results["redirected"] = True
            print(f"⚠️  REDIRECTED: {url} → {page.url}")
        
        # Take screenshot
        screenshot_path = f"{OUTPUT_DIR}/{name}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        results["screenshot"] = screenshot_path
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        # Check for visible error messages on the page
        error_selectors = [
            'text="Error"',
            'text="error"',
            '[class*="error"]',
            '[role="alert"]',
            '.error-message',
        ]
        
        for selector in error_selectors:
            try:
                error_elements = await page.query_selector_all(selector)
                if error_elements:
                    for elem in error_elements[:3]:  # Limit to first 3
                        text = await elem.inner_text()
                        if text and len(text) > 0:
                            results["errors"].append({
                                "type": "visible_error",
                                "selector": selector,
                                "text": text[:200]  # Limit text length
                            })
            except:
                pass
        
        # Check for specific data indicators
        print("\n📊 Data Check:")
        
        # Check for report data
        report_count = await page.query_selector_all('text=/report/i')
        print(f"   - Found {len(report_count)} elements mentioning 'report'")
        
        # Check for event data
        event_count = await page.query_selector_all('text=/event/i')
        print(f"   - Found {len(event_count)} elements mentioning 'event'")
        
        # Check for loading indicators
        loading = await page.query_selector_all('[class*="loading"], [class*="spinner"]')
        if loading:
            print(f"   - ⏳ Found {len(loading)} loading indicators")
        
        # Print console errors
        error_logs = [log for log in results["console_logs"] if log["type"] == "error"]
        if error_logs:
            print(f"\n❌ Console Errors ({len(error_logs)}):")
            for log in error_logs[:5]:  # Show first 5
                print(f"   - {log['text']}")
        
        # Print page errors
        if results["errors"]:
            print(f"\n❌ Page Errors ({len(results['errors'])}):")
            for err in results["errors"][:5]:  # Show first 5
                print(f"   - {err['type']}: {err.get('message', err.get('text', ''))[:100]}")
        
        if not error_logs and not results["errors"]:
            print("\n✅ No errors detected")
        
    except Exception as e:
        results["errors"].append({
            "type": "test_error",
            "message": str(e)
        })
        print(f"❌ Test failed: {e}")
        
        # Try to take screenshot anyway
        try:
            screenshot_path = f"{OUTPUT_DIR}/{name}_error.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            results["screenshot"] = screenshot_path
            print(f"📸 Error screenshot saved: {screenshot_path}")
        except:
            pass
    
    return results


async def main():
    """Main test runner"""
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n{'#'*60}")
    print(f"# Frontend Testing - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# Base URL: {BASE_URL}")
    print(f"# Output: {OUTPUT_DIR}/")
    print(f"{'#'*60}")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        # Test each page
        all_results = []
        for page_info in PAGES:
            result = await test_page(page, page_info)
            all_results.append(result)
        
        await browser.close()
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")
    
    for result in all_results:
        status = "❌" if result["errors"] else "✅"
        redirect = " (redirected)" if result["redirected"] else ""
        print(f"{status} {result['name']}: {result['final_url']}{redirect}")
        if result["errors"]:
            print(f"   Errors: {len(result['errors'])}")
    
    print(f"\n📁 All screenshots saved to: {OUTPUT_DIR}/")
    print(f"\n{'='*60}\n")
    
    # Write detailed report to file
    report_path = f"{OUTPUT_DIR}/test_report.txt"
    with open(report_path, 'w') as f:
        f.write(f"Frontend Test Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Base URL: {BASE_URL}\n\n")
        f.write("="*80 + "\n\n")
        
        for result in all_results:
            f.write(f"\nPage: {result['name']}\n")
            f.write(f"URL: {result['url']}\n")
            f.write(f"Final URL: {result['final_url']}\n")
            f.write(f"Redirected: {result['redirected']}\n")
            f.write(f"Status Code: {result['status_code']}\n")
            f.write(f"Screenshot: {result['screenshot']}\n")
            f.write(f"\nErrors ({len(result['errors'])}):\n")
            for err in result["errors"]:
                f.write(f"  - {err}\n")
            f.write(f"\nConsole Errors:\n")
            for log in [l for l in result["console_logs"] if l["type"] == "error"]:
                f.write(f"  - {log['text']}\n")
            f.write("\n" + "-"*80 + "\n")
    
    print(f"📄 Detailed report saved to: {report_path}\n")


if __name__ == "__main__":
    asyncio.run(main())
