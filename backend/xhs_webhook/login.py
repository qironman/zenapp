"""Bootstrap Xiaohongshu creator login for persistent Playwright profile."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_PROFILE_DIR = Path(os.getenv("XHS_PROFILE_DIR", "backend/data/xhs_profile"))
DEFAULT_PUBLISH_URL = os.getenv("XHS_PUBLISH_URL", "https://creator.xiaohongshu.com/publish/publish")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap Xiaohongshu login profile for ZenApp webhook.")
    parser.add_argument(
        "--profile-dir",
        default=str(DEFAULT_PROFILE_DIR),
        help="Playwright user data directory (default: backend/data/xhs_profile)",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_PUBLISH_URL,
        help="Creator page URL to open for login (default publish page).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run headless (not recommended for first login).",
    )
    args = parser.parse_args()

    profile_dir = Path(args.profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)

    print(f"[xhs-login] Using profile directory: {profile_dir}")
    print("[xhs-login] Browser will open. Please complete QR login in Xiaohongshu creator center.")
    print("[xhs-login] After login is done and publish page is visible, return to terminal and press Enter.")

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=args.headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(args.url, wait_until="domcontentloaded", timeout=90000)
            input()
        finally:
            context.close()

    print("[xhs-login] Profile saved. You can now run the webhook server.")


if __name__ == "__main__":
    main()
