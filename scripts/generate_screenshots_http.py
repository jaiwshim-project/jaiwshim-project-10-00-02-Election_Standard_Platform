#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Take screenshots of all platform pages via HTTP server
Requires: pip install selenium webdriver-manager
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Create assets directory
assets_dir = Path(__file__).parent.parent / "assets" / "screenshots"
assets_dir.mkdir(parents=True, exist_ok=True)

print("Starting HTTP server for screenshots...\n")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("Missing required packages.")
    print("Install with: pip install selenium webdriver-manager")
    sys.exit(1)

pages = [
    {'file': 'integrated-analysis.html', 'name': 'integrated-analysis', 'menu': 1},
    {'file': 'intelligence.html', 'name': 'intelligence', 'menu': 2},
    {'file': 'strategy.html', 'name': 'strategy', 'menu': 3},
    {'file': 'pledges.html', 'name': 'pledges', 'menu': 4},
    {'file': 'vehicle-strategy.html', 'name': 'vehicle-strategy', 'menu': 5},
    {'file': 'ai-chat.html', 'name': 'ai-chat', 'menu': 6},
    {'file': 'dashboard.html', 'name': 'dashboard', 'menu': 7},
    {'file': 'blog.html', 'name': 'blog', 'menu': 8},
    {'file': 'external-materials.html', 'name': 'external-materials', 'menu': 9},
    {'file': 'warroom.html', 'name': 'warroom', 'menu': 10},
    {'file': 'reports.html', 'name': 'reports', 'menu': 11},
    {'file': 'organization-chart.html', 'name': 'organization-chart', 'menu': 12},
    {'file': 'ai-premium.html', 'name': 'ai-premium', 'menu': 13},
    {'file': 'settings.html', 'name': 'settings', 'menu': 14}
]

# Start HTTP server in background
class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress log messages

os.chdir(Path(__file__).parent.parent)

server = HTTPServer(('localhost', 8000), QuietHTTPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

time.sleep(1)  # Give server time to start

# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('window-size=1280,720')

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for page in pages:
        try:
            # Navigate to page via HTTP
            url = f"http://localhost:8000/pages/{page['file']}"
            driver.get(url)

            # Wait for main content to load
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "main"))
                )
            except:
                pass

            # Additional wait for animations
            time.sleep(1)

            # Take screenshot
            screenshot_filename = f"menu-{str(page['menu']).zfill(2)}-{page['name']}.png"
            screenshot_path = assets_dir / screenshot_filename

            driver.save_screenshot(str(screenshot_path))

            print(f"[OK] Menu {str(page['menu']).zfill(2)}: {page['name']}")
            print(f"     {screenshot_path}\n")

        except Exception as e:
            print(f"[WARN] Menu {page['menu']}: {page['name']}")
            print(f"       Error: {str(e)}\n")

    driver.quit()
    print("Screenshots completed!")

except Exception as e:
    print(f"[ERROR] Browser error: {str(e)}")
    sys.exit(1)

finally:
    server.shutdown()
