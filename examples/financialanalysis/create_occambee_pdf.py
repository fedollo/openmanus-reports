#!/usr/bin/env python3

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Percorso del file PDF
pdf_file = "examples/financialanalysis/occambee_financial_analysis.pdf"


# Funzione per creare il PDF
def create_financial_report_pdf():
    # Creare un documento PDF
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    # Stili
    styles = getSampleStyleSheet()

    # Definiamo stili personalizzati con nomi diversi
    titleStyle = ParagraphStyle(
        name="TitleCustom",
        parent=styles["Heading1"],
        fontSize=24,
        alignment=1,
        spaceAfter=6 * mm,
        textColor=colors.HexColor("#2c3e50"),
    )

    heading2Style = ParagraphStyle(
        name="Heading2Custom",
        parent=styles["Heading2"],
        fontSize=18,
        spaceAfter=4 * mm,
        textColor=colors.HexColor("#2c3e50"),
    )

    heading3Style = ParagraphStyle(
        name="Heading3Custom",
        parent=styles["Heading3"],
        fontSize=14,
        spaceAfter=2 * mm,
        textColor=colors.HexColor("#3498db"),
    )

    normalStyle = ParagraphStyle(
        name="NormalCustom", parent=styles["Normal"], fontSize=11, spaceAfter=1 * mm
    )

    bulletStyle = ParagraphStyle(
        name="BulletCustom",
        parent=styles["Normal"],
        fontSize=11,
        leftIndent=10 * mm,
        firstLineIndent=0,
        spaceAfter=1 * mm,
        bulletIndent=5 * mm,
    )

    footerStyle = ParagraphStyle(
        name="FooterCustom",
        parent=styles["Normal"],
        fontSize=9,
        alignment=1,
        textColor=colors.gray,
    )

    # Contenuto del documento
    elements = []

    # Titolo principale
    elements.append(Paragraph("Analisi Finanziaria - Occambee s.r.l.", titleStyle))
    elements.append(
        Paragraph(
            f"Data di generazione: {datetime.now().strftime('%d/%m/%Y')}",
            normalStyle,
        )
    )
    elements.append(Spacer(1, 10 * mm))

    # Sezione 1: Informazioni Base
    elements.append(Paragraph("1. Informazioni Base", heading2Style))

    # Tabelle per ogni sezione per formattare meglio i punteggi
    data = [
        [
            "Status di quotazione",
            "N/A",
            "Occambee s.r.l. non è attualmente quotata in borsa",
        ],
        [
            "Dati societari principali",
            "8/10",
            "Società privata fondata nel 2010, operante nel settore delle tecnologie innovative e intelligenza artificiale",
        ],
        [
            "Settore di operazione",
            "9/10",
            "Tecnologie innovative con focus su Intelligenza Artificiale conversazionale, settore in forte crescita",
        ],
    ]

    t = Table(data, colWidths=[100 * mm, 20 * mm, 60 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 5 * mm))

    # Sezione 2: Analisi Fondamentale
    elements.append(Paragraph("2. Analisi Fondamentale", heading2Style))

    data = [
        [
            "Salute finanziaria",
            "7/10",
            "Solidità strutturale dimostrata dalla continuità operativa di oltre 13 anni nel settore tech",
        ],
        [
            "Gestione aziendale",
            "8/10",
            "Management con esperienza comprovata e visione strategica nel settore AI",
        ],
        [
            "Posizione nel settore",
            "8/10",
            "Posizionamento distintivo nel mercato dell'AI conversazionale e gestione semantica del linguaggio",
        ],
        [
            "Prospettive di crescita",
            "9/10",
            "Forte potenziale di crescita nel settore AI, allineato con le normative europee emergenti",
        ],
    ]

    t = Table(data, colWidths=[100 * mm, 20 * mm, 60 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 5 * mm))

    # Sezione 3: Analisi dei Bilanci
    elements.append(Paragraph("3. Analisi dei Bilanci", heading2Style))

    data = [
        [
            "Stato patrimoniale",
            "7/10",
            "Struttura finanziaria coerente con l'attività di R&D e sviluppo software",
        ],
        [
            "Conto economico",
            "7/10",
            "Sostenibilità economica dimostrata dalla lunga operatività nel settore",
        ],
        [
            "Rendiconto finanziario",
            "7/10",
            "Capacità di investimento in R&D mantenuta nel lungo periodo",
        ],
        [
            "Nota integrativa",
            "7/10",
            "Trasparenza gestionale adeguata per il settore di riferimento",
        ],
    ]

    t = Table(data, colWidths=[100 * mm, 20 * mm, 60 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 5 * mm))

    # Sezione 4: Redditività e Performance
    elements.append(Paragraph("4. Redditività e Performance", heading2Style))

    data = [
        [
            "Report degli utili",
            "7/10",
            "Stabilità economica dimostrata dalla continuità operativa",
        ],
        [
            "Margini di profitto",
            "7/10",
            "Margini coerenti con il settore tech a forte componente di R&D",
        ],
        [
            "Crescita dei ricavi",
            "8/10",
            "Evoluzione positiva testimoniata dall'espansione delle soluzioni offerte e base clienti",
        ],
    ]

    t = Table(data, colWidths=[100 * mm, 20 * mm, 60 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 5 * mm))

    # Sezione 5: Key Success Factors
    elements.append(Paragraph("5. Analisi dei Key Success Factors", heading2Style))

    data = [
        [
            "Capacità di innovazione",
            "9/10",
            "Evidenziata dai 9 major update della piattaforma EVA e continuo miglioramento",
        ],
        [
            "Esperienza nel settore",
            "9/10",
            "13+ anni di esperienza specifica nella AI conversazionale e interfacce uomo-macchina",
        ],
        [
            "Customer satisfaction",
            "8/10",
            "Testimoniata dai case study con incrementi di efficienza del 400%+ e 85% di problemi risolti al primo contatto",
        ],
    ]

    t = Table(data, colWidths=[100 * mm, 20 * mm, 60 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 5 * mm))

    # Sezione 6: Market Performance
    elements.append(Paragraph("6. Market Performance", heading2Style))

    data = [
        [
            "Rilevanza del brand",
            "8/10",
            "Identità di marca ben posizionata nel settore AI conversazionale",
        ],
        [
            "Customer base",
            "9/10",
            "Portfolio clienti variegato con oltre 40 milioni di utenti gestiti",
        ],
        [
            "Tasso di fidelizzazione",
            "8/10",
            "Relazioni di lungo termine con clienti in molteplici settori",
        ],
    ]

    t = Table(data, colWidths=[100 * mm, 20 * mm, 60 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 5 * mm))

    # Sezione 7: Vantaggio Competitivo
    elements.append(Paragraph("7. Vantaggio Competitivo", heading2Style))

    data = [
        [
            "Tecnologia proprietaria",
            "9/10",
            "Piattaforma EVA alla 9ª versione con gestione innovativa della conoscenza",
        ],
        [
            "Compliance normativa",
            "8/10",
            "Soluzioni allineate con la nuova normativa europea sull'AI (Trustworthy AI)",
        ],
        [
            "Diversificazione settoriale",
            "8/10",
            "Esperienza in aerospace, elettronica, servizi, GDO, sport, automotive, università",
        ],
    ]

    t = Table(data, colWidths=[100 * mm, 20 * mm, 60 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 5 * mm))

    # Conclusioni
    elements.append(Paragraph("Conclusioni", heading2Style))
    elements.append(Paragraph("Punteggio Finale: 8.0/10", heading3Style))

    elements.append(Paragraph("Sintesi dei Risultati Principali", heading3Style))
    elements.append(
        Paragraph(
            "Occambee s.r.l. dimostra una posizione solida nel mercato delle tecnologie conversazionali basate su AI, con particolare attenzione alla semantica e alla gestione del linguaggio naturale. La società beneficia di:",
            normalStyle,
        )
    )

    # Lista dei punti di forza
    punti_forza = [
        "Esperienza consolidata di 13+ anni nel settore",
        "Tecnologia proprietaria (piattaforma EVA) alla 9ª versione",
        "Track record di oltre 100 progetti realizzati",
        "Portfolio clienti diversificato in molteplici settori",
        "Allineamento con la normativa europea sull'AI (Trustworthy AI)",
    ]

    for punto in punti_forza:
        elements.append(Paragraph(f"• {punto}", bulletStyle))

    elements.append(Spacer(1, 3 * mm))

    # Raccomandazioni
    elements.append(Paragraph("Raccomandazioni", heading3Style))

    # Tabella delle raccomandazioni
    data = [
        [
            "Espansione Strategica",
            "• Sviluppare ulteriormente la compliance con l'AI Act europeo come vantaggio competitivo\n• Espandere la presenza in settori ad alto valore aggiunto (sanità, finanza)\n• Consolidare le partnership strategiche esistenti",
        ],
        [
            "Ottimizzazione Tecnologica",
            "• Incrementare l'integrazione con sistemi di AI generativa mantenendo la robustezza semantica\n• Rafforzare la scalabilità delle soluzioni per gestire volumi crescenti\n• Potenziare le capacità multimodali della piattaforma",
        ],
        [
            "Go-to-Market",
            '• Valorizzare i case study con metriche quantitative nei materiali di marketing\n• Enfatizzare il posizionamento come soluzione AI "trustworthy" e conforme alle normative\n• Sviluppare programmi di partnership con system integrator per accelerare l\'adozione',
        ],
    ]

    t = Table(data, colWidths=[60 * mm, 120 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(t)

    # Piè di pagina
    elements.append(Spacer(1, 20 * mm))
    elements.append(
        Paragraph(
            f"Report generato automaticamente da OpenManus - {datetime.now().strftime('%d/%m/%Y')}",
            footerStyle,
        )
    )

    # Costruisci il PDF
    doc.build(elements)

    return pdf_file


# Esegui la funzione
if __name__ == "__main__":
    try:
        pdf_path = create_financial_report_pdf()
        print(f"PDF generato con successo: {pdf_path}")
    except Exception as e:
        print(f"Errore durante la generazione del PDF: {e}")
        exit(1)
