
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def generate_pdf(html: str, output: str = "output.pdf"):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            await page.set_content(
                html,
                wait_until="load"
            )

            await page.pdf(
                path=output,
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={
                    "top": "10mm",
                    "bottom": "10mm",
                    "left": "10mm",
                    "right": "10mm"
                }
            )

            print(f"PDF generated: {Path(output).resolve()}")
        finally:
            await browser.close()


async def main():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #1e293b;
            }

            h1 {
                color: #1d4ed8;
                text-align: center;
            }

            table {
                width: 100%;
                border-collapse: collapse;
            }

            th, td {
                padding: 12px;
                border: 1px solid #cbd5e1;
                text-align: left;
            }

            th {
                background: #dbeafe;
            }
        </style>
    </head>
    <body>
        <h1>Student Admit Card</h1>

        <p><strong>Name:</strong> Rahim Ahmed</p>
        <p><strong>Class:</strong> Eleven</p>
        <p><strong>Roll:</strong> 1025</p>

        <table>
            <tr>
                <th>Subject</th>
                <th>Exam Date</th>
                <th>Time</th>
            </tr>
            <tr>
                <td>Bangla</td>
                <td>27/10/2026</td>
                <td>11:00 AM</td>
            </tr>
            <tr>
                <td>English</td>
                <td>28/10/2026</td>
                <td>11:00 AM</td>
            </tr>
        </table>
    </body>
    </html>
    """

    await generate_pdf(html, "admit-card.pdf")


if __name__ == "__main__":
    asyncio.run(main())
