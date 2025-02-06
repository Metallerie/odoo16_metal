# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceOcrAutomation(http.Controller):
#     @http.route('/invoice_ocr_automation/invoice_ocr_automation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_ocr_automation/invoice_ocr_automation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_ocr_automation.listing', {
#             'root': '/invoice_ocr_automation/invoice_ocr_automation',
#             'objects': http.request.env['invoice_ocr_automation.invoice_ocr_automation'].search([]),
#         })

#     @http.route('/invoice_ocr_automation/invoice_ocr_automation/objects/<model("invoice_ocr_automation.invoice_ocr_automation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_ocr_automation.object', {
#             'object': obj
#         })
