from playwright.async_api import async_playwright
import json
from videodownloader.login import save_cookies
import os

async def capture_video(videourl,website_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
            ]
        )
        context = await browser.new_context()

        # تحميل الكوكيز
        if not os.path.exists(f"videodownloader/cookies/{website_name}.json"):
            await save_cookies(f'https://{website_name}/login',website_name)
        with open(f"videodownloader/cookies/{website_name}.json", "r") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.route("**/*", lambda route: (
        route.abort() if route.request.resource_type in ["image", "font"]
        or any(ext in route.request.url for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"])
        else route.continue_()
        ))
        user_agent =  await page.evaluate('navigator.userAgent')

        video_url = {"value": None}   

        def handle_request(request):
            url = request.url
            if (".m3u8" in url or ".mp4" in url) and video_url["value"] is None:
                video_url["value"] = url

        context.on("request", handle_request)

        await page.goto(videourl, wait_until="commit", timeout=120000)

        try:
            await page.click("button[class*='play'], vjs-big-play-button", timeout=20000)
        except:
            pass

        for _ in range(20):  
            if video_url["value"]:
                break
            await page.wait_for_timeout(50)


        if "login" in page.url.lower():
            print("⚠️ الكوكيز منتهية — يجب تسجيل الدخول من جديد")
            await save_cookies(page.url,website_name)
            return await capture_video(videourl, website_name)


        return video_url["value"], user_agent