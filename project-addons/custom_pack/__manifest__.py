# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Pack management & importation from magento 2.0',
    'summary': '',
    'version': '11.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'comunitea.com',
    'author': 'Comunitea',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'product',
        'connector_magento'
    ],
    'data': [
        'views/product_template.xml',
        'wizard/sale_order_add_pack.xml',
        'views/sale.xml',
        'security/ir.model.access.csv'
    ],
}
