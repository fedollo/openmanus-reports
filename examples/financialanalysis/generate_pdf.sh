#!/bin/bash

# Percorso del file Markdown
MD_FILE="examples/financialanalysis/shakazamba_financial_analysis.md"
HTML_FILE="examples/financialanalysis/shakazamba_financial_analysis.html"

# Assicuriamoci che il file Markdown esista
if [ ! -f "$MD_FILE" ]; then
    echo "Errore: File Markdown non trovato: $MD_FILE"
    exit 1
fi

# Converti Markdown in HTML usando pandoc se disponibile, altrimenti usa un semplice script
if command -v pandoc &> /dev/null; then
    echo "Utilizzo pandoc per convertire Markdown in HTML..."
    pandoc "$MD_FILE" -o "$HTML_FILE" --standalone --metadata title="Analisi Finanziaria - SHAKAZAMBA srl" \
        -c "data:text/css;base64,$(cat <<- END | base64
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.5; font-size: 11pt; color: #333; }
        h1 { color: #2c3e50; font-weight: bold; text-align: center; font-size: 24pt; margin-bottom: 20px; }
        h2 { color: #2c3e50; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; font-size: 18pt; margin-top: 30px; }
        h3 { color: #3498db; font-weight: bold; font-size: 14pt; margin-top: 20px; }
        strong { font-weight: bold; }
        em { font-style: italic; }
        ul { margin-left: 20px; }
        .footer { text-align: center; margin-top: 50px; font-size: 9pt; color: #666; }
END
)"
else
    echo "Pandoc non trovato, utilizzo un approccio alternativo..."
    # Crea un semplice HTML
    cat > "$HTML_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Analisi Finanziaria - SHAKAZAMBA srl</title>
    <style>
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.5; font-size: 11pt; color: #333; padding: 20px; }
        h1 { color: #2c3e50; font-weight: bold; text-align: center; font-size: 24pt; margin-bottom: 20px; }
        h2 { color: #2c3e50; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; font-size: 18pt; margin-top: 30px; }
        h3 { color: #3498db; font-weight: bold; font-size: 14pt; margin-top: 20px; }
        strong { font-weight: bold; }
        em { font-style: italic; }
        ul { margin-left: 20px; }
        .footer { text-align: center; margin-top: 50px; font-size: 9pt; color: #666; }
    </style>
</head>
<body>
$(cat "$MD_FILE" | sed -e 's/^# \(.*\)/<h1>\1<\/h1>/g' \
                       -e 's/^## \(.*\)/<h2>\1<\/h2>/g' \
                       -e 's/^### \(.*\)/<h3>\1<\/h3>/g' \
                       -e 's/^\- \(.*\)/<li>\1<\/li>/g' \
                       -e 's/^\*\*\(.*\)\*\*/<strong>\1<\/strong>/g' \
                       -e 's/^\*\(.*\)\*/<em>\1<\/em>/g' \
                       -e 's/^$/<p><\/p>/g')
<div class="footer">Report generato da OpenManus - $(date +%d/%m/%Y)</div>
</body>
</html>
EOF
fi

echo "HTML creato in: $HTML_FILE"

# Apri il file HTML in Safari
open -a Safari "$HTML_FILE"

echo "Il file HTML è stato aperto in Safari."
echo "Per salvare come PDF:"
echo "1. Premi Cmd + P"
echo "2. Seleziona 'Salva come PDF'"
echo "3. Scegli come nome file: shakazamba_financial_analysis.pdf"
echo "4. Assicurati di selezionare 'Formato A4' e 'Margini personalizzati' (20mm su tutti i lati)"
echo "5. Clicca su 'Salva'"
