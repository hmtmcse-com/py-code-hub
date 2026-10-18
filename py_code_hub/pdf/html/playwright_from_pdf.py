
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "result-card.html"
OUTPUT_FILE = BASE_DIR / "result-card.pdf"

TOTAL = 50


async def generate_pdf():
    if not HTML_FILE.exists():
        raise FileNotFoundError(f"HTML file not found: {HTML_FILE}")

    async with async_playwright() as playwright:
        print("Starting Chromium...", flush=True)

        browser = await playwright.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            print("Loading HTML and assets...", flush=True)

            # Load local HTML, CSS, images and fonts
            await page.goto(
                HTML_FILE.as_uri(),
                wait_until="domcontentloaded",
                timeout=15000
            )

            print("Duplicating result cards...", flush=True)

            await page.evaluate(
                """
                (total) => {
                    const original = document.body.innerHTML;
                    const container = document.createElement("div");

                    for (let i = 0; i < total; i++) {
                        const item = document.createElement("div");
                        item.className = "pdf-card";
                        item.innerHTML = original;
                        container.appendChild(item);
                    }

                    document.body.replaceChildren(container);
                }
                """,
                TOTAL
            )

            # PDF print styling
            await page.add_style_tag(content="""
                @page {
                    size: A4;
                    margin: 0;
                }

                @media print {
                    html, body {
                        margin: 0;
                        padding: 0;
                    }

                    .pdf-card {
                        break-inside: avoid;
                        page-break-inside: avoid;
                        break-after: page;
                        page-break-after: always;
                    }

                    .pdf-card:last-child {
                        break-after: auto;
                        page-break-after: auto;
                    }
                }
            """)

            print("Waiting for fonts...", flush=True)

            await asyncio.wait_for(
                page.evaluate("document.fonts.ready"),
                timeout=15
            )

            print("Generating PDF...", flush=True)

            await asyncio.wait_for(
                page.pdf(
                    path=str(OUTPUT_FILE),
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={
                        "top": "0",
                        "right": "0",
                        "bottom": "0",
                        "left": "0"
                    }
                ),
                timeout=60
            )

            print(f"PDF generated successfully: {OUTPUT_FILE}", flush=True)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(generate_pdf())
