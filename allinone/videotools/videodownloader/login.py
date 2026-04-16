from playwright.async_api import async_playwright
import json
import asyncio

async def save_cookies(login_url,website_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto(login_url, wait_until="domcontentloaded")

        print("🔐 الرجاء تسجيل الدخول...")

        while True:
            # إذا تغير الرابط فهذا يعني تسجيل الدخول نجح
            url = page.url.lower()
            if "login" not in url and "signin" not in url:
                break

            # إذا ظهر عنصر يدل على تسجيل الدخول
            if await page.locator("text=Logout").count() > 0:
                break
            if await page.locator("text=Dashboard").count() > 0:
                break

            await asyncio.sleep(1)


        # حفظ الكوكيز
        cookies = await context.cookies()
        with open(f"videodownloader/cookies/{website_name}.json", "w") as f:
            json.dump(cookies, f)

        print("✅ تم حفظ الكوكيز بنجاح")

        await browser.close()