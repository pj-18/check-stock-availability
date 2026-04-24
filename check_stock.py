from playwright.sync_api import sync_playwright
import sys
import os

def check_puma_stock():
    available_sizes = []
    
    # Read target sizes from sizes.txt
    try:
        with open("sizes.txt", "r") as f:
            target_sizes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("sizes.txt not found! Exiting.")
        return available_sizes

    
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
            print(f"Page title: {page.title()}")

            page.screenshot(path="debug.png")

            page.wait_for_selector('label', timeout=15000)

            labels = page.locator('label').all()
            print(f"Total labels found: {len(labels)}")
            for label in labels:
                text = label.inner_text().strip()
                input_id = label.get_attribute("for")
                if input_id:
                    input_el = page.locator(f"#{input_id}")
                    class_attr = input_el.get_attribute("class") if input_el.count() > 0 else "N/A"
                    is_disabled = input_el.is_disabled() if input_el.count() > 0 else "N/A"
                    print(f"Label: '{text}' | for='{input_id}' | disabled={is_disabled} | class='{class_attr}'")
                if text in target_sizes:
                    print(f"Found label '{text}'.")

                    input_id = label.get_attribute("for")
                    if input_id:
                        input_el = page.locator(f"#{input_id}")
                        if input_el.count() > 0:
                            is_disabled = input_el.is_disabled()
                            print(f"Input associated with '{text}' disabled state: {is_disabled}")

                            if not is_disabled:
                                print(f"STATUS: {text} IS AVAILABLE")
                                available_sizes.append(text)
                            else:
                                print(f"STATUS: {text} IS OUT OF STOCK")

        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Page URL at error: {page.url}")
            print(f"Page title at error: {page.title()}")
            
        browser.close()
        return available_sizes

if __name__ == "__main__":
    sizes = check_puma_stock()
    if sizes:
        # We write to GITHUB_OUTPUT to pass the text securely to the next step
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"available_sizes={', '.join(sizes)}\n")
        sys.exit(0)
    else:
        sys.exit(1)
