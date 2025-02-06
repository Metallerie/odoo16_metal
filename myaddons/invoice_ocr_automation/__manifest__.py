# -*- coding: utf-8 -*-
{
    'name': "Automatisation OCR Factures Fournisseurs",
    'version': '1.0',
    'depends': ['base', 'account'],
    'author': "Franck compagnie",
    'category': 'Accounting',
    'summary': 'Automatise l’OCR des factures fournisseurs pour mise à jour des informations',
    'data': [
        'security/ir.model.access.csv',
        'views/ocr_data_view.xml',
        'views/supplier_ocr_config_views.xml',
        'views/menu_views.xml',
        'data/cron_data.xml',
        
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
