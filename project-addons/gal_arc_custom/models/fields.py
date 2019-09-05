# © 2019 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.tools import html_escape as escape


class Contact(models.AbstractModel):
    _inherit = 'ir.qweb.field.contact'

    @api.model
    def value_to_html(self, value, options):
        if not value.exists():
            return False

        opf = options and options.get('fields') or ["name", "address", "phone", "mobile", "email"]
        value = value.sudo().with_context(show_address=True)
        name_get = value.name_get()[0][1]

        val = {
            'name': name_get.split("\n")[0],
            'address': escape("\n".join(name_get.split("\n")[1:])).strip(),
            'phone': value.phone,
            'mobile': value.mobile,
            'city': value.city,
            'country_id': value.country_id.display_name,
            'website': value.website,
            'email': value.email,
            'fields': opf,
            'object': value,
            'options': options
        }
        if value.parent_id and value.name == value.parent_id.name:
            val['name'] = value.name
        return self.env['ir.qweb'].render('base.contact', val, **options.get('template_options'))
