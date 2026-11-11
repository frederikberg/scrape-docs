# scrape-docs

Scrape documentation sites to Markdown for offline reading.

## Overview

Converts JavaScript-rendered documentation websites to offline Markdown files. Uses Playwright (headless browser) to render pages and Trafilatura to extract clean content.

## Installation

```bash
pipx install git+https://github.com/frederikberg/scrape-docs.git
```

Requirements: Python 3.9+

Chromium browser auto-downloads to `~/.cache/ms-playwright/` on first run.

## Usage

```bash
# Basic usage
scrape-docs https://docs.example.com/page -o output.md

# Auto-generated filename from URL
scrape-docs https://docs.gitlab.com/ee/ci/

# Adjust wait time for slow-loading sites
scrape-docs https://site.com/docs -o output.md -w 10000
```

**Options:**
- `-o, --output` - Output file path (default: auto-generated from URL)
- `-w, --wait` - Wait time in milliseconds after page load (default: 5000)

## Tested Sites

**Works:**
- docs.gitlab.com
- example.com

**Timeout issues:**
- platform.openai.com/docs

Your mileage may vary - modern docs sites have varying levels of JavaScript complexity.

## How It Works

- **Playwright** launches headless chromium browser, navigates to URL, waits for page load
- **Trafilatura** extracts main content from rendered HTML to Markdown

Timeout is 60 seconds - pages that don't fully load by then will fail.

## Limitations

- Single pages only (no site-wide crawling)
- Some sites may timeout
- No authentication support
- Large pages may produce incomplete extraction

## Dependencies

See pyproject.toml for current versions.

## License

MIT
