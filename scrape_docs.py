#!/usr/bin/env python3
"""
Documentation scraper using Playwright + Trafilatura.
Scrapes modern JavaScript-heavy documentation sites to clean Markdown.

Installation:
  pipx install git+https://github.com/FrederikBerg/scrape-docs.git

On first run, chromium browser (~100MB) is automatically downloaded to
~/.cache/ms-playwright/ if not already installed.

See pyproject.toml for dependencies.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import trafilatura
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: Required packages not installed.", file=sys.stderr)
    print("Install with: pipx install git+https://github.com/FrederikBerg/scrape-docs.git", file=sys.stderr)
    sys.exit(1)


def ensure_chromium():
    """Ensure chromium browser is installed for Playwright on first run."""
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
            except Exception:
                # Chromium not found, install it
                print("First run: Installing chromium browser (~100MB)...", file=sys.stderr)
                print("This is a one-time download to ~/.cache/ms-playwright/", file=sys.stderr)
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                print("Chromium installed successfully!", file=sys.stderr)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error installing chromium: {e}", file=sys.stderr)
        sys.exit(1)


def scrape_page(url: str, output_file: Path, wait_time: int = 5000) -> bool:
    """Scrape a single page and save to Markdown."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"Loading {url}...")
            page.goto(url, wait_until='networkidle', timeout=60000)  # 60s timeout for heavy sites
            page.wait_for_timeout(wait_time)  # Extra wait for dynamic content

            html = page.content()
            browser.close()

        print("Extracting Markdown...")
        markdown = trafilatura.extract(
            html,
            output_format='markdown',
            include_links=True,
            include_images=True,
            include_tables=True,
            include_formatting=True,
        )

        if not markdown:
            print("Warning: No content extracted from page", file=sys.stderr)
            return False

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(markdown, encoding='utf-8')
        print(f"Saved to: {output_file}")
        return True

    except PlaywrightTimeout:
        print(f"Error: Timeout loading {url}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


def main():
    # Ensure chromium is installed on first run
    ensure_chromium()

    parser = argparse.ArgumentParser(
        description="Scrape documentation sites to Markdown using Playwright + Trafilatura",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://platform.openai.com/docs -o openai-docs.md
  %(prog)s https://docs.gitlab.com/ee/ci/ -o gitlab-ci.md -w 10000
        """
    )
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('-o', '--output', help='Output file path (default: auto-generated from URL)')
    parser.add_argument('-w', '--wait', type=int, default=5000,
                       help='Wait time in milliseconds after page load (default: 5000)')

    args = parser.parse_args()

    # Auto-generate output filename if not provided
    if args.output:
        output_file = Path(args.output)
    else:
        parsed = urlparse(args.url)
        filename = f"{parsed.netloc.replace('.', '-')}.md"
        output_file = Path(filename)

    success = scrape_page(args.url, output_file, args.wait)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
