from odoo import models, fields, api
from ..utils.ocr_processing import extract_text, parse_invoice
import os

class InvoiceProcessing(models.Model):
    _name = 'invoice.processing'
    _description = 'Traitement OCR des Factures'

    @api.model
    def _ocr_acquisition(self, file_path):
        """Traite le fichier via OCR et renvoie le texte extrait"""
        text = extract_text(file_path)
        return text

    @api.model
    def _update_supplier_from_text(self, text, supplier_config):
        """Mise à jour de res.partner en fonction du texte OCR"""
        data = parse_invoice(text, {})
        partner = self.env['res.partner'].search([('siret', '=', data.get('siret'))], limit=1)
        
        if partner:
            partner.write({key: value for key, value in data.items() if value is not None})
        else:
            self.env['res.partner'].create({key: value for key, value in data.items() if value is not None})

