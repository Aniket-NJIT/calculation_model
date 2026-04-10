import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module", autouse=True)
def start_server():
    # Start the FastAPI server in the background for E2E tests
    process = subprocess.Popen(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(2)  # Give the server a moment to start up
    yield
    process.terminate() # Kill server after tests

def test_calculator_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000/")

        # Test Addition
        page.fill("#a", "10")
        page.fill("#b", "5")
        page.get_by_text("Add", exact=True).click()
        page.wait_for_selector("text=Calculation Result: 15")
        
        # Test Subtraction
        page.fill("#a", "10")
        page.fill("#b", "5")
        page.get_by_text("Subtract", exact=True).click()
        page.wait_for_selector("text=Calculation Result: 5")

        # Test Multiplication
        page.fill("#a", "10")
        page.fill("#b", "5")
        page.get_by_text("Multiply", exact=True).click()
        page.wait_for_selector("text=Calculation Result: 50")

        # Test Successful Division
        page.fill("#a", "10")
        page.fill("#b", "5")
        page.get_by_text("Divide", exact=True).click()
        page.wait_for_selector("text=Calculation Result: 2")

        # Test Division by Zero
        page.fill("#a", "10")
        page.fill("#b", "0")
        page.get_by_text("Divide", exact=True).click()
        page.wait_for_selector("text=Error: Cannot divide by zero!")

        browser.close()