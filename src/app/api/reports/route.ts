import { NextResponse } from 'next/server';
import puppeteer from 'puppeteer';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { title, content } = body;

        // Avvia il browser
        const browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        // Crea una nuova pagina
        const page = await browser.newPage();

        // Imposta il contenuto HTML
        await page.setContent(`
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <title>${title}</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              line-height: 1.6;
              margin: 40px;
              color: #333;
            }
            h1 {
              color: #2c3e50;
              border-bottom: 2px solid #3498db;
              padding-bottom: 10px;
              margin-bottom: 20px;
            }
            h2 {
              color: #34495e;
              margin-top: 30px;
            }
            p {
              margin-bottom: 15px;
            }
            .section {
              margin-bottom: 30px;
            }
            .highlight {
              background-color: #f8f9fa;
              padding: 15px;
              border-radius: 5px;
              margin: 15px 0;
            }
            .market-size {
              font-weight: bold;
              color: #27ae60;
            }
            .competition {
              color: #e74c3c;
            }
            .opportunity {
              color: #2980b9;
            }
            .footer {
              margin-top: 50px;
              padding-top: 20px;
              border-top: 1px solid #eee;
              font-size: 0.9em;
              color: #666;
            }
          </style>
        </head>
        <body>
          ${content}
        </body>
      </html>
    `);

        // Genera il PDF
        const pdf = await page.pdf({
            format: 'A4',
            printBackground: true,
            margin: {
                top: '20mm',
                right: '20mm',
                bottom: '20mm',
                left: '20mm'
            }
        });

        // Chiudi il browser
        await browser.close();

        // Restituisci il PDF come risposta
        return new NextResponse(pdf, {
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': `attachment; filename="${title.toLowerCase().replace(/\s+/g, '-')}.pdf"`
            }
        });

    } catch (error) {
        console.error('Errore nella generazione del report:', error);
        return NextResponse.json(
            { error: 'Errore nella generazione del report' },
            { status: 500 }
        );
    }
}
