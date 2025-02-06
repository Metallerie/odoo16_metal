import pytesseract
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path
import re
import os
import tempfile
import logging
import base64


# Configuration du logger pour écrire dans le fichier de log d’Odoo
log_file_path = "/home/odoo/metal-odoo16-p8171/odoo-server.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_temp_pdf(binary_data, file_name="temp_pdf"):
    """
    Décoder les données PDF base64 et les sauvegarder dans un fichier temporaire.
    """
    try:
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, file_name + ".pdf")
        with open(pdf_path, "wb") as f:
            f.write(base64.b64decode(binary_data))
        logger.info(f"Fichier PDF temporaire sauvegardé à : {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier PDF temporaire : {e}")
        return None

def convert_pdf_to_images(pdf_binary_data, output_folder="/home/odoo/metal-odoo16-p8171/uploads/invoice_supplier"):
    """
    Convertit un PDF (encodé en base64) en images PNG et enregistre chaque page dans output_folder.
    """
    # Sauvegarde temporaire du PDF
    pdf_path = save_temp_pdf(pdf_binary_data, "uploaded_invoice")
    
    if not pdf_path:
        logger.error("Le fichier PDF n'a pas pu être sauvegardé. Processus annulé.")
        return []

    try:
        logger.info(f"Début de la conversion du PDF en images depuis : {pdf_path}")
        images = convert_from_path(pdf_path, dpi=300)
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f"invoice_page_{i + 1}.png")
            image.save(image_path, "PNG")
            if os.path.exists(image_path):
                logger.info(f"Image sauvegardée et accessible : {image_path}")
            else:
                logger.error(f"Image non trouvée après la sauvegarde : {image_path}")
            image_paths.append(image_path)
        
        os.remove(pdf_path)  # Suppression du fichier temporaire PDF
        logger.info(f"Fichier PDF temporaire supprimé : {pdf_path}")
        
        return image_paths
    except Exception as e:
        logger.error(f"Erreur lors de la conversion du PDF en images : {e}")
        return []
        
        
        
def extract_text_from_image(image_path):
    """
    Extrait le texte d'une image avec OCR.
    """
    image = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(image.convert('L'))
    image = enhancer.enhance(2.0).point(lambda x: 0 if x < 128 else 255, '1')
    return pytesseract.image_to_string(image, lang='fra')

def extract_text(file_path):
    """
    Extrait le texte d'un fichier (PDF ou image).
    Gère les PDF en convertissant chaque page en image avant OCR.
    """
    text = ""
    if file_path.lower().endswith('.pdf'):
        # Convertir chaque page du PDF en une image et extraire le texte
        image_paths = convert_pdf_to_images(file_path)
        for image_path in image_paths:
            text += extract_text_from_image(image_path) + "\n"
            os.remove(image_path)  # Supprimer l'image après traitement
    else:
        # Si ce n'est pas un PDF, traiter directement comme une image
        text = extract_text_from_image(file_path)
    
    return text

def parse_invoice(text, supplier_config):
    """
    Extrait des informations spécifiques d'un texte OCR (SIRET, TVA, Numéro de facture).
    """
    siret = re.search(r"SIRET\s?:\s?(\d{14})", text)
    vat = re.search(r"TVA\s+intracommunautaire\s?:\s?(FR\d+)", text)
    invoice_number = re.search(r"N°\s?Facture\s?:\s?(\d+)", text)

    return {
        "siret": siret.group(1) if siret else None,
        "vat": vat.group(1) if vat else None,
        "invoice_number": invoice_number.group(1) if invoice_number else None
    }
