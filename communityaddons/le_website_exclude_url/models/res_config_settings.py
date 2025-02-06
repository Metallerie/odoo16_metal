from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    le_excl_sitemap_url = fields.Text(string="Exclude from Sitemap",related='website_id.le_excl_sitemap_url', readonly=False)