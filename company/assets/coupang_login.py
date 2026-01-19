import asyncio
import sys
sys.path.insert(0, '/Users/dongin/Library/Python/3.9/lib/python/site-packages')

from playwright.async_api import async_playwright

async def login_coupang():
    async with async_playwright() as p:
        # 브라우저를 headless=False로 실행하면 화면에서 볼 수 있음
        # 여기서는 headless=True로 스크린샷으로 확인
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        print("1. 쿠팡 윙 로그인 페이지 접속 중...")
        await page.goto('https://wing.coupang.com')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        # 현재 페이지 스크린샷
        await page.screenshot(path='/Users/dongin/repositories/ai_company/company/assets/coupang_step1.png', full_page=True)
        print("📸 스크린샷 저장: coupang_step1.png")
        print(f"현재 URL: {page.url}")

        # 페이지 내용 확인
        content = await page.content()

        # 로그인 폼 찾기
        login_form = await page.query_selector('input[type="text"], input[type="email"], input[name="username"], input[name="email"], input[id="username"], input[id="email"]')
        password_form = await page.query_selector('input[type="password"]')

        if login_form and password_form:
            print("2. 로그인 폼 발견! 로그인 시도 중...")

            # 아이디 입력
            await login_form.fill('xxx@email.com')
            await asyncio.sleep(0.5)

            # 비밀번호 입력
            await password_form.fill('xxx')
            await asyncio.sleep(0.5)

            await page.screenshot(path='/Users/dongin/repositories/ai_company/company/assets/coupang_step2.png', full_page=True)
            print("📸 스크린샷 저장: coupang_step2.png (입력 완료)")

            # 로그인 버튼 찾기 및 클릭
            login_btn = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("로그인"), button:has-text("Login")')
            if login_btn:
                print("3. 로그인 버튼 클릭...")
                await login_btn.click()
                await asyncio.sleep(3)
                await page.wait_for_load_state('networkidle')

                await page.screenshot(path='/Users/dongin/repositories/ai_company/company/assets/coupang_step3.png', full_page=True)
                print("📸 스크린샷 저장: coupang_step3.png (로그인 후)")
                print(f"로그인 후 URL: {page.url}")
            else:
                print("❌ 로그인 버튼을 찾을 수 없습니다")
        else:
            print("로그인 폼을 찾을 수 없습니다. 페이지 구조 확인 필요")
            print(f"login_form: {login_form}, password_form: {password_form}")

            # 모든 input 요소 찾기
            inputs = await page.query_selector_all('input')
            print(f"페이지의 input 요소 수: {len(inputs)}")
            for i, inp in enumerate(inputs):
                inp_type = await inp.get_attribute('type')
                inp_name = await inp.get_attribute('name')
                inp_id = await inp.get_attribute('id')
                print(f"  input[{i}]: type={inp_type}, name={inp_name}, id={inp_id}")

        await browser.close()
        print("\n완료!")

asyncio.run(login_coupang())
