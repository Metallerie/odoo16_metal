# -*- coding: utf-8 -*-
#################################################################################
# Author      : Cubicle Technolabs
# Copyright(c): Cubicle Technolabs
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{   
    # App information
    'name': 'Advance SEO Sitemap',
    'version': '1.0',
    'summary': 'This app is used to generate advance SEO sitemap.',
    'category': 'Website',
    'license': 'OPL-1',
    'images': ['static/description/cover_image.jpg'],

     # Dependencies
    'depends': ['website_sale'],
    
    #views
    'data': [
        'views/product_template_view.xml',
        'views/product_public_category_view.xml',
        'views/website_page_view.xml'
    ],

     'qweb': [
    ],

    # Author
    'author': 'Cubicle Technolabs',
    'website': '',
    'maintainer': 'Cubicle Technolabs',
    'installable': True,
    'auto_install': False,
}
