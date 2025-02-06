# -*- coding: utf-8 -*-
# from odoo import http


# class VariantPicture2023(http.Controller):
#     @http.route('/variant_picture_2023/variant_picture_2023', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/variant_picture_2023/variant_picture_2023/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('variant_picture_2023.listing', {
#             'root': '/variant_picture_2023/variant_picture_2023',
#             'objects': http.request.env['variant_picture_2023.variant_picture_2023'].search([]),
#         })

#     @http.route('/variant_picture_2023/variant_picture_2023/objects/<model("variant_picture_2023.variant_picture_2023"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('variant_picture_2023.object', {
#             'object': obj
#         })
