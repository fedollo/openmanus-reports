from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

# Configurazione dei font
font_config = FontConfiguration()

# Carica il file HTML
html = HTML("shakazamba_analysis_pdf.html")

# Crea il PDF
html.write_pdf(
    "shakazamba_marketing_analysis.pdf",
    stylesheets=[
        CSS(
            string="""
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                font-size: 24pt;
                margin-bottom: 1cm;
            }
            h2 {
                color: #2c3e50;
                font-size: 18pt;
                margin-top: 1.5cm;
                margin-bottom: 0.5cm;
                border-bottom: 1px solid #3498db;
                padding-bottom: 0.3cm;
            }
            .section {
                margin-bottom: 1cm;
            }
            .metric-box {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 0.5cm;
                margin: 0.3cm 0;
                border-radius: 4px;
            }
            .recommendation {
                margin: 0.5cm 0;
                padding-left: 0.5cm;
                border-left: 4px solid #3498db;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 0.5cm 0;
            }
            th, td {
                border: 1px solid #dee2e6;
                padding: 0.3cm;
                text-align: left;
            }
            th {
                background-color: #f8f9fa;
            }
        """
        )
    ],
    font_config=font_config,
)

print("PDF generato con successo: shakazamba_marketing_analysis.pdf")
