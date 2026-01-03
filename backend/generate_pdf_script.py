"""
Standalone script to generate PDF from HTML using Playwright.
Called by pdf_engine.py via subprocess to avoid asyncio loop conflicts.
"""
import sys
import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright

async def generate_pdf(html_path: str, pdf_path: str):
    print(f"Starting PDF generation for {html_path}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            file_uri = Path(html_path).absolute().as_uri()
            print(f"Loading URL: {file_uri}")
            
            await page.goto(file_uri, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(1000)
            
            print(f"Writing PDF to {pdf_path}")
            await page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={
                    "top": "10mm",
                    "bottom": "10mm",
                    "left": "8mm",
                    "right": "8mm"
                }
            )
            
            await browser.close()
            print("PDF Generation Complete")
            return True
            
    except Exception as e:
        print(f"PDF GENERATION ERROR: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", required=True, help="Path to input HTML")
    parser.add_argument("--out", required=True, help="Path to output PDF")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(generate_pdf(args.html, args.out))
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)
