from weasyprint import HTML, CSS

# Option A: Convert an HTML string directly with embedded CSS
html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @bottom-right {
                content: counter(page) " of " counter(pages);
                font-family: Arial, sans-serif;
                font-size: 9pt;
            }
        }
        body {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #333;
            line-height: 1.6;
        }
        h1 {
            color: #1a5f7a;
            border-bottom: 2px solid #1a5f7a;
            padding-bottom: 5px;
        }
        .card {
            background-color: #f8f9fa;
            border-left: 4px solid #1a5f7a;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .page-break {
            page-break-before: always;
        }
    </style>
</head>
<body>
    <h1>Invoice / Document Title</h1>
    <p>This PDF was generated from standard HTML & CSS using <strong>WeasyPrint</strong>.</p>

    <div class="card">
        <h3>Summary Details</h3>
        <p>Status: Completed</p>
        <p>Type: Python Automated Export</p>
    </div>

    <div class="page-break"></div>

    <h1>Page 2 Content</h1>
    <p>This content appears on the second page thanks to the <code>page-break-before: always;</code> CSS rule.</p>
    
    
    
</body>
</html>
"""

# Render string to PDF file
HTML(string=html_content).write_pdf("output_from_string.pdf")
print("Saved output_from_string.pdf successfully!")
