from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import os
import tempfile
import logging
from pdf2image import convert_from_path

_logger = logging.getLogger(__name__)

class SupplierOCRConfig(models.Model):
    _name = 'supplier.ocr.config'
    _description = 'Configuration OCR des Fournisseurs'

    # Champs principaux
    name = fields.Char("Nom du Fournisseur", required=True)
    siret = fields.Char("SIRET", required=True)
    vat_number = fields.Char("Numéro de TVA")
    field_positions = fields.Text("Positions des Champs")  # Zones spécifiques pour OCR
    footer_fees = fields.Boolean("Frais en Pied de Page", default=False)

    # Champs pour le fichier modèle et le téléchargement manuel
    image_facture = fields.Binary("Facture Modèle", attachment=True, store=True, help="Téléchargez une facture modèle pour définir les zones.")
    file_name = fields.Char("Nom du fichier modèle")  # Nom du fichier image pour référence
    file_upload = fields.Binary("Télécharger une autre facture", attachment=True, store=True)
    file_name_upload = fields.Char("Nom du fichier", default="facture_par_defaut.pdf")

    # Champ calculé pour afficher la dernière image convertie
    last_attachment = fields.Binary("Dernière Page de la Facture", compute='_compute_last_attachment', store=False)

    @api.depends('file_upload')
    def _compute_last_attachment(self):
        """Récupère le dernier fichier attaché pour cet enregistrement"""
        for record in self:
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', 'supplier.ocr.config'),
                ('res_id', '=', record.id)
            ], order="id desc", limit=1)
            record.last_attachment = attachment.datas if attachment else None

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import os
import tempfile
import logging
from pdf2image import convert_from_path
from datetime import datetime

_logger = logging.getLogger(__name__)

class SupplierOCRConfig(models.Model):
    _name = 'supplier.ocr.config'
    _description = 'Configuration OCR des Fournisseurs'

    # Champs principaux
    name = fields.Char("Nom du Fournisseur", required=True)
    siret = fields.Char("SIRET", required=True)
    vat_number = fields.Char("Numéro de TVA")
    field_positions = fields.Text("Positions des Champs")  # Zones spécifiques pour OCR
    footer_fees = fields.Boolean("Frais en Pied de Page", default=False)

    # Champs pour le fichier modèle et le téléchargement manuel
    image_facture = fields.Binary("Facture Modèle", attachment=True, store=True, help="Téléchargez une facture modèle pour définir les zones.")
    file_name = fields.Char("Nom du fichier modèle")  # Nom du fichier image pour référence
    file_upload = fields.Binary("Télécharger une autre facture", attachment=True, store=True)
    file_name_upload = fields.Char("Nom du fichier", default="facture_par_defaut.pdf")

    # Champ calculé pour afficher la dernière image convertie
    last_attachment = fields.Binary("Dernière Page de la Facture", compute='_compute_last_attachment', store=False)

    @api.depends('file_upload')
    def _compute_last_attachment(self):
        """Récupère le dernier fichier attaché pour cet enregistrement"""
        for record in self:
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', 'supplier.ocr.config'),
                ('res_id', '=', record.id)
            ], order="id desc", limit=1)
            record.last_attachment = attachment.datas if attachment else None

    def action_acquisition_manuel(self):
        """Lancer le processus d'OCR pour le fichier téléchargé"""
        _logger.info("[DEBUG] Bouton d'acquisition manuel activé.")
        
        if not self.file_upload:
            raise ValueError("Veuillez télécharger un fichier avant de lancer l'acquisition.")

        # Si le champ `file_name_upload` est vide, lui assigner un nom par défaut
        if not self.file_name_upload:
            self.file_name_upload = "facture_par_defaut.pdf"

        # Enregistrer temporairement le fichier PDF
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, self.file_name_upload)
        pdf_content = base64.b64decode(self.file_upload)
        
        with open(file_path, 'wb') as f:
            f.write(pdf_content)
        
        _logger.info(f"[DEBUG] Fichier PDF temporaire sauvegardé à : {file_path}")

        # Convertir et sauvegarder chaque page comme attachement
        try:
            images = convert_from_path(file_path, dpi=200)
            for i, image in enumerate(images):
                # Définir le nom de l'image en fonction du modèle `model_nom-du-fournisseur_date.png`
                supplier_name = self.name.replace(" ", "_")
                current_date = datetime.today().strftime('%Y-%m-%d')
                image_name = f"model_{supplier_name}_{current_date}.png"
                image_path = os.path.join(temp_dir, image_name)
                
                image.save(image_path, "PNG")
                
                with open(image_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read())
                    attachment = self.env['ir.attachment'].create({
                        'name': image_name,
                        'type': 'binary',
                        'datas': img_data,
                        'res_model': 'supplier.ocr.config',
                        'res_id': self.id,
                        'mimetype': 'image/png',
                    })
                    _logger.info(f"[DEBUG] Image sauvegardée comme attachement avec l'ID : {attachment.id} et nom : {image_name}")
                
                self.file_name = image_name  # Dernière image convertie
                os.remove(image_path)  # Supprimer le fichier temporaire après sauvegarde
        except Exception as e:
            _logger.error(f"[ERROR] Erreur lors de la conversion du PDF en images : {e}")
            raise ValueError("Erreur lors de la conversion du PDF en images. Vérifiez que le fichier est un PDF valide.")
        
        os.remove(file_path)  # Supprimer le fichier temporaire PDF

        # Forcer la mise à jour du champ calculé pour afficher la dernière image
        self._compute_last_attachment()

    def action_telecharger_facture(self):
        """Télécharger le fichier PDF original depuis le champ `file_upload`"""
        if not self.file_upload:
            raise UserError(_("Aucun fichier disponible pour le téléchargement."))

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content?model=supplier.ocr.config&id={self.id}&field=file_upload&download=true&filename={self.file_name_upload}",
            'target': 'self',
        }
