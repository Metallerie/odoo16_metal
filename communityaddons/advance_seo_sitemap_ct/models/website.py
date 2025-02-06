# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools
from odoo.http import request
from odoo.osv.expression import FALSE_DOMAIN
from odoo.addons.website.models.ir_http import sitemap_qs2dom

class website(models.Model):
    _inherit = 'website'

    def enumerate_pages(self, query_string=None, force=False):
        """ Available pages in the website/CMS. This is mostly used for links
            generation and can be overridden by modules setting up new HTML
            controllers for dynamic pages (e.g. blog).
            By default, returns template views marked as pages.
            :param str query_string: a (user-provided) string, fetches pages
                                     matching the string
            :returns: a list of mappings with two keys: ``name`` is the displayable
                      name of the resource (page), ``url`` is the absolute URL
                      of the same.
            :rtype: list({name: str, url: str})
        """

        router = request.httprequest.app.get_db_router(request.db)
        # Force enumeration to be performed as public user
        url_set = set()

        sitemap_endpoint_done = set()

        for rule in router.iter_rules():
            if 'sitemap' in rule.endpoint.routing:
                if rule.endpoint in sitemap_endpoint_done:
                    continue
                sitemap_endpoint_done.add(rule.endpoint)

                func = rule.endpoint.routing['sitemap']
                if func is False:
                    continue
                for loc in func(self.env, rule, query_string):
                    yield loc
                continue

            if not self.rule_is_enumerable(rule):
                continue

            converters = rule._converters or {}
            if query_string and not converters and (query_string not in rule.build([{}], append_unknown=False)[1]):
                continue
            values = [{}]
            # converters with a domain are processed after the other ones
            convitems = sorted(
                converters.items(),
                key=lambda x: (hasattr(x[1], 'domain') and (x[1].domain != '[]'), rule._trace.index((True, x[0]))))

            for (i, (name, converter)) in enumerate(convitems):
                newval = []
                for val in values:
                    query = i == len(convitems) - 1 and query_string
                    if query:
                        r = "".join([x[1] for x in rule._trace[1:] if not x[0]])  # remove model converter from route
                        query = sitemap_qs2dom(query, r, self.env[converter.model]._rec_name)
                        if query == FALSE_DOMAIN:
                            continue
                    for value_dict in converter.generate(uid=self.env.uid, dom=query, args=val):
                        newval.append(val.copy())
                        value_dict[name] = value_dict['loc']
                        del value_dict['loc']
                        newval[-1].update(value_dict)
                values = newval

            for value in values:
                domain_part, url = rule.build(value, append_unknown=False)
                if not query_string or query_string.lower() in url.lower():
                    page = {'loc': url}
                    if value.get('category', False):
                        categ_id = value.get('category')[0]
                        category = request.env['product.public.category'].sudo().search([('id','=',categ_id)])
                        if category:
                            if category.priority:
                                page.update({'priority':category.priority})
                            if category.frequency:
                                page.update({'changefreq': category.frequency})

                    if value.get('product', False):
                        prod_id = value.get('product')[0]
                        product = request.env['product.template'].sudo().search([('id','=',prod_id)])
                        if product:
                            if product.priority:
                                page.update({'priority':product.priority})
                            if product.frequency:
                                page.update({'changefreq': product.frequency})
                    for key, val in value.items():
                        if key.startswith('__'):
                            page[key[2:]] = val
                    if url in ('/sitemap.xml',):
                        continue
                    if url in url_set:
                        continue
                    url_set.add(url)
                    yield page

        # '/' already has a http.route & is in the routing_map so it will already have an entry in the xml
        domain = [('url', '!=', '/')]
        if not force:
            domain += [('website_indexed', '=', True)]
            # is_visible
            domain += [('website_published', '=', True), '|', ('date_publish', '=', False),
                       ('date_publish', '<=', fields.Datetime.now())]

        if query_string:
            domain += [('url', 'like', query_string)]

        pages = self.get_website_pages(domain)

        for page in pages:
            record = {'loc': page['url'], 'id': page['id'], 'name': page['name']}
            if page.frequency:
                record.update({'changefreq': page.frequency})
            if page.priority:
                record.update({'priority': page.priority})
            if page.view_id and page.view_id.priority != 16:
                record['__priority'] = min(round(page.view_id.priority / 32.0, 1), 1)
            if page['write_date']:
                record['__lastmod'] = page['write_date'].date()
            yield record