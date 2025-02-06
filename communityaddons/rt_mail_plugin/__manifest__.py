{
    'name': 'Email Management System',
    'version': '13.0.1.0.0',
    'category': 'Emails',
    'sequence': 1,
    'author': 'Rolustech',
    'summary': 'Email Management System',
    'website': 'https://www.rolustech.com/',
    'description': """
    """,
    'depends': ['contacts'],
    'data': [
        'views/email_record.xml',
        'views/menu_item.xml',
        'views/email_tags.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/email_templates.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
