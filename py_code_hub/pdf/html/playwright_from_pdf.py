
import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


BASE_DIR = Path(__file__).resolve().parent


async def generate_pdf(
    html_file: str | Path,
    output_file: str | Path,
    total: int = 1,
    paper_size: str = "A4"
):
    html_path = Path(html_file).resolve()
    output_path = Path(output_file).resolve()

    if not html_path.is_file():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    if total < 1:
        raise ValueError("Total must be at least 1")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        print("Starting Chromium...", flush=True)

        browser = await playwright.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            print("Loading HTML and assets...", flush=True)

            await page.goto(
                html_path.as_uri(),
                wait_until="load",
                timeout=30000
            )

            if total > 1:
                print(f"Duplicating {total} copies...", flush=True)

                await page.evaluate(
                    """
                    (total) => {
                        const original = document.body.innerHTML;
                        const container = document.createElement("div");

                        for (let i = 0; i < total; i++) {
                            const item = document.createElement("div");
                            item.className = "pdf-page";
                            item.innerHTML = original;
                            container.appendChild(item);
                        }

                        document.body.replaceChildren(container);
                    }
                    """,
                    total
                )

            await page.add_style_tag(content="""
                @media print {
                    html, body {
                        margin: 0;
                        padding: 0;
                    }

                    .pdf-page {
                        break-inside: avoid;
                        page-break-inside: avoid;
                        break-after: page;
                    }

                    .pdf-page:last-child {
                        break-after: auto;
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
                    path=str(output_path),
                    format=paper_size,
                    print_background=True,
                    prefer_css_page_size=False,
                    margin={
                        "top": "0",
                        "right": "0",
                        "bottom": "0",
                        "left": "0"
                    }
                ),
                timeout=120
            )

            print(f"PDF generated: {output_path}", flush=True)

        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate PDF from HTML using Playwright"
    )

    parser.add_argument(
        "html",
        nargs="?",
        default=str(BASE_DIR / "result-card.html"),
        help="Input HTML file"
    )

    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output PDF file"
    )

    parser.add_argument(
        "-n", "--total",
        type=int,
        default=150,
        help="Number of copies (default: 50)"
    )

    parser.add_argument(
        "-s", "--size",
        default="A4",
        help="Paper size (default: A4)"
    )

    args = parser.parse_args()

    html_path = Path(args.html).resolve()

    if args.output:
        output_path = Path(args.output).resolve()
    else:
        output_path = html_path.with_suffix(".pdf")

    asyncio.run(
        generate_pdf(
            html_file=html_path,
            output_file=output_path,
            total=args.total,
            paper_size=args.size
        )
    )


if __name__ == "__main__":
    main()
