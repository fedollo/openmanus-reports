import io

from app.logger import logger
from PIL import Image


def resize_image(image_data: bytes, max_size_mb: int = 4) -> bytes:
    """
    Ridimensiona un'immagine per assicurarsi che non superi la dimensione massima specificata.

    Args:
        image_data: Dati dell'immagine in formato bytes
        max_size_mb: Dimensione massima in MB (default 4MB per lasciare margine)

    Returns:
        bytes: Dati dell'immagine ridimensionata
    """
    try:
        # Apri l'immagine
        img = Image.open(io.BytesIO(image_data))

        # Converti in RGB se necessario
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Calcola il fattore di ridimensionamento
        max_size_bytes = max_size_mb * 1024 * 1024
        quality = 95

        while True:
            # Salva l'immagine in un buffer
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            size = buffer.tell()

            if size <= max_size_bytes or quality <= 5:
                return buffer.getvalue()

            # Riduci la qualità e riprova
            quality -= 5
            buffer.close()

    except Exception as e:
        logger.error(f"Errore durante il ridimensionamento dell'immagine: {e}")
        return image_data
