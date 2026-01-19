import asyncio
import sys
sys.path.insert(0, '/Users/dongin/Library/Python/3.9/lib/python/site-packages')

from playwright.async_api import async_playwright

async def capture_full_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 860, 'height': 800})

        # Load HTML file
        await page.goto('file:///Users/dongin/repositories/ai_company/company/assets/product_detail_page.html')

        # Wait for content to load
        await page.wait_for_load_state('networkidle')

        # Capture full page screenshot
        await page.screenshot(
            path='/Users/dongin/repositories/ai_company/company/assets/detail_page_full.png',
            full_page=True
        )

        print("✅ 상세페이지 이미지 생성 완료!")
        print("📁 저장 위치: /Users/dongin/repositories/ai_company/company/assets/detail_page_full.png")

        await browser.close()

asyncio.run(capture_full_page())
