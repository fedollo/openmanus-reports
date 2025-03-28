#!/usr/bin/env python3

import os
import sys
from datetime import datetime

import markdown
from weasyprint import CSS, HTML

# Percorsi dei file
md_file = "examples/financialanalysis/shakazamba_financial_analysis.md"
html_temp = "examples/financialanalysis/temp.html"
pdf_file = "examples/financialanalysis/shakazamba_financial_analysis.pdf"

# CSS per la formattazione
css = """
@page {
    size: A4;
    margin: 20mm;
}
body {
    font-family: "Helvetica Neue", Arial, sans-serif;
    line-height: 1.5;
    margin: 0;
    font-size: 11pt;
    color: #333;
}
h1 {
    color: #2c3e50;
    font-weight: bold;
    text-align: center;
    font-size: 24pt;
    margin-bottom: 20px;
}
h2 {
    color: #2c3e50;
    font-weight: bold;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
    font-size: 18pt;
    margin-top: 30px;
}
h3 {
    color: #3498db;
    font-weight: bold;
    font-size: 14pt;
    margin-top: 20px;
}
strong {
    font-weight: bold;
}
em {
    font-style: italic;
}
ul {
    margin-left: 20px;
}
.score-high {
    color: #27ae60;
    font-weight: bold;
}
.score-medium {
    color: #f39c12;
    font-weight: bold;
}
.score-low {
    color: #e74c3c;
    font-weight: bold;
}
.score-na {
    color: #7f8c8d;
    font-weight: bold;
}
.footer {
    text-align: center;
    margin-top: 50px;
    font-size: 9pt;
    color: #666;
}
"""

# Converti Markdown a HTML
try:
    print("Lettura del file Markdown...")
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    print("Conversione da Markdown a HTML...")
    html = markdown.markdown(md_content, extensions=["extra"])

    # Aggiungi colori ai punteggi
    html = html.replace(
        "<strong>Punteggio:</strong> 8",
        '<strong>Punteggio:</strong> <span class="score-high">8</span>',
    )
    html = html.replace(
        "<strong>Punteggio:</strong> 9",
        '<strong>Punteggio:</strong> <span class="score-high">9</span>',
    )
    html = html.replace(
        "<strong>Punteggio:</strong> 10",
        '<strong>Punteggio:</strong> <span class="score-high">10</span>',
    )

    html = html.replace(
        "<strong>Punteggio:</strong> 5",
        '<strong>Punteggio:</strong> <span class="score-medium">5</span>',
    )
    html = html.replace(
        "<strong>Punteggio:</strong> 6",
        '<strong>Punteggio:</strong> <span class="score-medium">6</span>',
    )
    html = html.replace(
        "<strong>Punteggio:</strong> 7",
        '<strong>Punteggio:</strong> <span class="score-medium">7</span>',
    )

    html = html.replace(
        "<strong>Punteggio:</strong> 1",
        '<strong>Punteggio:</strong> <span class="score-low">1</span>',
    )
    html = html.replace(
        "<strong>Punteggio:</strong> 2",
        '<strong>Punteggio:</strong> <span class="score-low">2</span>',
    )
    html = html.replace(
        "<strong>Punteggio:</strong> 3",
        '<strong>Punteggio:</strong> <span class="score-low">3</span>',
    )
    html = html.replace(
        "<strong>Punteggio:</strong> 4",
        '<strong>Punteggio:</strong> <span class="score-low">4</span>',
    )

    html = html.replace(
        "<strong>Punteggio:</strong> N/A",
        '<strong>Punteggio:</strong> <span class="score-na">N/A</span>',
    )

    # Crea HTML completo con CSS
    html_complete = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Analisi Finanziaria - SHAKAZAMBA srl</title>
        <style>
            {css}
        </style>
    </head>
    <body>
        {html}
        <div class="footer">
            Report generato da OpenManus - {datetime.now().strftime('%d/%m/%Y')}
        </div>
    </body>
    </html>
    """

    # Salva HTML temporaneo
    with open(html_temp, "w", encoding="utf-8") as f:
        f.write(html_complete)

    print("HTML temporaneo creato con successo.")

    # Converti HTML a PDF usando WeasyPrint
    print("Conversione da HTML a PDF...")
    HTML(html_temp).write_pdf(pdf_file, stylesheets=[CSS(string=css)])
    print(f"PDF generato con successo: {pdf_file}")

    # Rimuovi il file HTML temporaneo
    os.remove(html_temp)
    print("File HTML temporaneo rimosso.")

except Exception as e:
    print(f"Errore durante la conversione: {e}")
    sys.exit(1)

sys.exit(0)
