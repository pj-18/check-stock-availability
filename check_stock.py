from playwright.sync_api import sync_playwright
import sys
import os

def check_puma_stock():
    available_sizes = []

    try:
        with open("sizes.txt", "r") as f:
            target_sizes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("sizes.txt not found! Exiting.")
        return [], []

    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        url = "https://in.puma.com/in/en/pd/puma-x-rcb-2026-mens-vk18-official-jersey/714345"
        print(f"Navigating to {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_selector('label[data-size]', timeout=15000)

            size_labels = page.locator('label[data-size]').all()
            print(f"Size labels found: {len(size_labels)}")
            for label in size_labels:
                text = label.locator('span[data-content="size-value"]').inner_text().strip()
                is_disabled = label.get_attribute("data-disabled") == "true"
                print(f"Size: '{text}' | disabled={is_disabled}")
                if text in target_sizes and not is_disabled:
                    print(f"STATUS: {text} IS AVAILABLE")
                    available_sizes.append(text)

        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Page URL at error: {page.url}")
            print(f"Page title at error: {page.title()}")
            
        browser.close()
        return available_sizes, target_sizes

if __name__ == "__main__":
    sizes, checked = check_puma_stock()
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"available_sizes={', '.join(sizes)}\n")
            f.write(f"checked_sizes={', '.join(checked)}\n")
    sys.exit(0)
