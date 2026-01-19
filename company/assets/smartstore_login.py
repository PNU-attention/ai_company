import asyncio
import sys
sys.path.insert(0, '/Users/dongin/Library/Python/3.9/lib/python/site-packages')

from playwright.async_api import async_playwright

async def login_smartstore():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        print("1. 스마트스토어 센터 접속 중...")
        await page.goto('https://sell.smartstore.naver.com/')
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)

        print("2. '로그인하기' 버튼 클릭...")
        login_link = await page.query_selector('a:has-text("로그인하기"), button:has-text("로그인하기")')
        if login_link:
            await login_link.click()
            await asyncio.sleep(3)
            await page.wait_for_load_state('networkidle')

        print(f"현재 URL: {page.url}")

        # 네이버 커머스 로그인 페이지
        if 'accounts.commerce.naver.com' in page.url:
            print("\n3. 네이버 커머스 로그인 페이지...")
            await asyncio.sleep(2)

            # placeholder로 입력 필드 찾기
            id_input = await page.query_selector('input[placeholder*="아이디"], input[placeholder*="이메일"]')
            pw_input = await page.query_selector('input[placeholder*="비밀번호"], input[type="password"]')

            if not id_input:
                # 모든 input 찾아보기
                inputs = await page.query_selector_all('input')
                print(f"   input 요소 수: {len(inputs)}")
                for inp in inputs:
                    inp_type = await inp.get_attribute('type')
                    if inp_type == 'text' or inp_type == 'email':
                        id_input = inp
                    elif inp_type == 'password':
                        pw_input = inp

            if id_input and pw_input:
                print("4. 로그인 폼 발견! 입력 중...")

                # 아이디 입력
                await id_input.click()
                await asyncio.sleep(0.3)
                await page.keyboard.type('xxx@email.com', delay=30)
                await asyncio.sleep(0.5)

                # 비밀번호 입력
                await pw_input.click()
                await asyncio.sleep(0.3)
                await page.keyboard.type('xxx', delay=30)
                await asyncio.sleep(0.5)

                await page.screenshot(path='/Users/dongin/repositories/ai_company/company/assets/smartstore_step3.png', full_page=True)
                print("📸 스크린샷 저장: smartstore_step3.png (입력 완료)")

                # 로그인 버튼 클릭
                login_btn = await page.query_selector('button:has-text("로그인")')
                if login_btn:
                    print("5. 로그인 버튼 클릭...")
                    await login_btn.click()
                    await asyncio.sleep(5)
                    await page.wait_for_load_state('networkidle')

                    await page.screenshot(path='/Users/dongin/repositories/ai_company/company/assets/smartstore_step4.png', full_page=True)
                    print(f"📸 스크린샷 저장: smartstore_step4.png (로그인 시도 후)")
                    print(f"로그인 후 URL: {page.url}")

                    # 로그인 성공 여부 확인
                    if 'sell.smartstore.naver.com' in page.url and 'login' not in page.url:
                        print("\n✅ 로그인 성공!")
                    else:
                        print("\n⚠️ 로그인 실패 또는 추가 인증 필요")
                        # 에러 메시지 확인
                        error_msg = await page.query_selector('.error, .alert, [class*="error"]')
                        if error_msg:
                            error_text = await error_msg.text_content()
                            print(f"   에러: {error_text}")
                else:
                    print("❌ 로그인 버튼을 찾을 수 없습니다")
            else:
                print(f"❌ 로그인 입력 필드를 찾을 수 없습니다 (id_input: {id_input}, pw_input: {pw_input})")

        await browser.close()
        print("\n완료!")

asyncio.run(login_smartstore())
