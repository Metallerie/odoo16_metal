from odoo import models, fields, api
import logging
import pytesseract
from PIL import Image
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class OCRDataAcquisition(models.Model):
    _name = 'ocr.data.acquisition'
    _description = 'Acquisition de Données OCR pour Factures'

    name = fields.Char(string="Nom du Fichier", required=True)
    image_path = fields.Char(string="Chemin de l'Image", required=True)
    ocr_text = fields.Text(string="Texte OCR", readonly=True)
    @api.model
    def process_image(self):
        # Logique de traitement OCR
        pass

    @api.model
    def save_ocr_data(self):
        # Logique de sauvegarde des données OCR extraites
        pass

    # Table One2Many pour les données extraites
    extracted_data_ids = fields.One2many(
        'ocr.extracted.data', 'ocr_data_id', string="Données Extraites"
    )

    def process_image(self):
        """Traitement de l'image pour l'extraction de données OCR avec position"""
        try:
            image = Image.open(self.image_path)
            ocr_results = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Efface les données extraites précédentes
            self.extracted_data_ids.unlink()

            # Enregistre chaque champ extrait avec la position
            for i in range(len(ocr_results['text'])):
                field_name = ocr_results['text'][i]
                pos_x = ocr_results['left'][i]
                pos_y = ocr_results['top'][i]

                if field_name.strip():  # Enregistrer uniquement les champs non vides
                    self.env['ocr.extracted.data'].create({
                        'ocr_data_id': self.id,
                        'field_name': field_name,
                        'extracted_value': ocr_results['text'][i],
                        'position_x': pos_x,
                        'position_y': pos_y,
                    })
        except Exception as e:
            _logger.error(f"Erreur lors du traitement OCR : {e}")
            raise ValidationError(f"Erreur lors du traitement OCR : {e}")

    def extract_footer_data(self):
        """Extraction des informations spécifiques en pied de page."""
        footer_data = [d for d in self.extracted_data_ids if d.position_y > 800]  # Position Y indicative
        for data in footer_data:
            if 'transport' in data.field_name.lower():
                _logger.info("Donnée de transport détectée en pied de page")

    def validate_extracted_data(self):
        """Valide les données extraites pour vérifier la cohérence et les mentions légales."""
        required_fields = ['Adresse', 'SIRET', 'Numéro de Facture', 'Total HT', 'Taux de TVA', 'Montant TVA', 'Total TTC']
        missing_fields = [field for field in required_fields if field not in self.extracted_data_ids.mapped('field_name')]

        if missing_fields:
            raise ValidationError(f"Les champs suivants sont manquants ou incorrects : {', '.join(missing_fields)}")
        
        try:
            total_ht = sum(float(d.extracted_value) for d in self.extracted_data_ids if d.field_name == 'Total HT')
            total_ttc = sum(float(d.extracted_value) for d in self.extracted_data_ids if d.field_name == 'Total TTC')
            tva = total_ttc - total_ht
            _logger.info(f"Total HT : {total_ht}, Total TTC : {total_ttc}, TVA calculée : {tva}")
        except ValueError:
            raise ValidationError("Les valeurs des montants ne sont pas numériques.")

class OCRExtractedData(models.Model):
    _name = 'ocr.extracted.data'
    _description = 'Données Extraites par OCR'

    ocr_data_id = fields.Many2one(
        'ocr.data.acquisition', string="Facture OCR", required=True
    )
    field_name = fields.Char(string="Intitulé du Champ", required=True)
    extracted_value = fields.Text(string="Donnée Extraite")
    position_x = fields.Integer(string="Position X")
    position_y = fields.Integer(string="Position Y")
